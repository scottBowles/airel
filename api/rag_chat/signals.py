"""Re-embed RAG content automatically when its source data changes.

`post_save` covers field edits (including FKs such as `Character.race` and
`Place.parent`); `m2m_changed` covers the M2M relationships the content processors read,
since `post_save` does not fire for those.

Invariant: signal handlers must not write back to the source model — the hash guard is
naturally self-terminating because process_content writes only to ContentChunk (and
EmbeddingRevision), never to the models below, so a save can't trigger another save.

Bulk operations (seeding, imports) should run inside `disconnect_embedding_signals()`
and re-embed afterwards with the management commands.
"""

import logging
from contextlib import contextmanager

from django.db import transaction
from django.db.models.signals import m2m_changed, post_save

from association.models import Association
from character.models import Character
from item.models import Artifact, Item
from nucleus.models import GameLog
from place.models import Place
from race.models import Race

from .tasks import process_content

logger = logging.getLogger(__name__)

# Model -> the content_type string process_content and CONTENT_PROCESSORS use.
CONTENT_TYPES = {
    GameLog: "gamelog",
    Character: "character",
    Place: "place",
    Item: "item",
    Artifact: "artifact",
    Race: "race",
    Association: "association",
}

# M2M fields whose changes alter the owning model's embedded content.
TRACKED_M2M_FIELDS = [
    Character.associations,
    GameLog.places_set_in,
    Artifact.items,
]

M2M_ACTIONS = {"post_add", "post_remove", "post_clear"}

DISPATCH_UID_PREFIX = "rag_chat.embedding"


def enqueue_processing(content_type: str, object_id) -> None:
    """Queue process_content once the current transaction commits.

    Waiting for the commit means the worker reads the saved data, not the row as it was
    before the transaction. A broker outage is logged rather than raised, so a save never
    fails because Redis is down; the next save or a manual reprocess catches it up.
    """

    def send():
        try:
            process_content.delay(content_type, str(object_id))
        except Exception:
            logger.exception(
                "Could not queue process_content for %s %s", content_type, object_id
            )

    transaction.on_commit(send)


# Signal handlers must not write back to the source model — the hash guard is naturally
# self-terminating because process_content writes only to ContentChunk.
def embed_on_save(sender, instance, raw=False, **kwargs):
    if raw:  # loaddata: fixtures are loaded as-is
        return
    enqueue_processing(CONTENT_TYPES[sender], instance.pk)


# Signal handlers must not write back to the source model — the hash guard is naturally
# self-terminating because process_content writes only to ContentChunk.
def embed_on_m2m_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action not in M2M_ACTIONS:
        return
    if not reverse:
        # e.g. character.associations.add(...): the instance's content changed.
        enqueue_processing(CONTENT_TYPES[type(instance)], instance.pk)
        return
    # e.g. association.characters.add(...): the instance is the other side and pk_set
    # holds the changed owners. A reverse clear() sends no pk_set, so it can't be traced.
    for pk in pk_set or ():
        enqueue_processing(CONTENT_TYPES[model], pk)


def _receivers():
    """(signal, handler, sender, dispatch_uid) for every embedding signal."""
    for model in CONTENT_TYPES:
        yield (
            post_save,
            embed_on_save,
            model,
            f"{DISPATCH_UID_PREFIX}.save.{model._meta.label}",
        )
    for field in TRACKED_M2M_FIELDS:
        through = field.through
        yield (
            m2m_changed,
            embed_on_m2m_change,
            through,
            f"{DISPATCH_UID_PREFIX}.m2m.{through._meta.label}",
        )


def connect_embedding_signals() -> None:
    for signal, handler, sender, uid in _receivers():
        signal.connect(handler, sender=sender, dispatch_uid=uid, weak=False)


def disconnect_embedding_signals_now() -> None:
    for signal, handler, sender, uid in _receivers():
        signal.disconnect(handler, sender=sender, dispatch_uid=uid)


@contextmanager
def disconnect_embedding_signals():
    """Suppress automatic re-embedding for the duration of a bulk operation.

    Disconnects every embedding signal on enter and reconnects them on exit, even if the
    block raises. Saves made inside the block are not queued for embedding. Nesting is
    safe: only the outermost block reconnects.
    """
    global _suppress_depth
    if _suppress_depth == 0:
        disconnect_embedding_signals_now()
    _suppress_depth += 1
    try:
        yield
    finally:
        _suppress_depth -= 1
        if _suppress_depth == 0:
            connect_embedding_signals()


_suppress_depth = 0
