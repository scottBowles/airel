"""Entity search by name and alias, in Postgres (pg_trgm).

Serves the command palette and the entity picker. A hit matches the query on the entity's
name or one of its aliases, by substring or by trigram similarity, so partial names and
small typos both work. Hits rank exact matches first, then prefix matches, then other
substring matches, then the rest by similarity.
"""

from dataclasses import dataclass
from enum import Enum

from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from django.db.models import (
    Case,
    Exists,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Greatest

# Lower bound on similarity for a hit that isn't a substring match, taken over the larger
# of pg_trgm's similarity and word similarity. 0.4 keeps one-letter typos ("Siren" for
# "Siraen" scores 0.5, "Port Veel" for "Port Veil" 0.7) and drops words that only share
# their first two letters ("Siren" against "Signal Flare" scores 0.33).
MIN_SIMILARITY = 0.4
DEFAULT_LIMIT = 10
MAX_LIMIT = 50

# Rank tiers, best first.
EXACT, PREFIX, CONTAINS, SIMILAR = range(4)


class EntityType(Enum):
    ARTIFACT = "Artifact"
    ASSOCIATION = "Association"
    CHARACTER = "Character"
    ITEM = "Item"
    PLACE = "Place"
    RACE = "Race"


@dataclass(frozen=True)
class SearchHit:
    type: EntityType
    pk: int
    name: str
    description: str | None
    thumbnail: str | None
    rank: int
    score: float


def _models():
    from association.models import Association
    from character.models import Character
    from item.models import Artifact, Item
    from place.models import Place
    from race.models import Race

    return {
        EntityType.ARTIFACT: Artifact,
        EntityType.ASSOCIATION: Association,
        EntityType.CHARACTER: Character,
        EntityType.ITEM: Item,
        EntityType.PLACE: Place,
        EntityType.RACE: Race,
    }


def _search_model(model, query: str, limit: int):
    from nucleus.models import Alias

    # Alias.base_<model>s is the reverse side of Entity.aliases.
    aliases = Alias.objects.filter(
        **{f"base_{model._meta.model_name}s": OuterRef("pk")}
    )

    def alias_has(lookup):
        return Exists(aliases.filter(**{f"name__{lookup}": query}))

    def similarity(field):
        return Greatest(
            TrigramSimilarity(field, query), TrigramWordSimilarity(query, field)
        )

    alias_score = Subquery(
        aliases.annotate(s=similarity("name")).order_by("-s").values("s")[:1],
        output_field=FloatField(),
    )

    return (
        model.objects.annotate(
            search_rank=Case(
                When(Q(name__iexact=query) | alias_has("iexact"), then=Value(EXACT)),
                When(
                    Q(name__istartswith=query) | alias_has("istartswith"),
                    then=Value(PREFIX),
                ),
                When(
                    Q(name__icontains=query) | alias_has("icontains"),
                    then=Value(CONTAINS),
                ),
                default=Value(SIMILAR),
                output_field=IntegerField(),
            ),
            search_score=Greatest(
                similarity("name"), Coalesce(alias_score, Value(0.0))
            ),
        )
        .filter(Q(search_rank__lt=SIMILAR) | Q(search_score__gte=MIN_SIMILARITY))
        .order_by("search_rank", "-search_score", "name")
        .only("pk", "name", "description", "thumbnail_id", "image_ids")[:limit]
    )


def search_entities(
    query: str,
    types: list[EntityType] | None = None,
    limit: int = DEFAULT_LIMIT,
) -> list[SearchHit]:
    """Entities whose name or an alias matches `query`, best first, at most `limit`."""
    query = query.strip()
    limit = max(0, min(limit, MAX_LIMIT))
    if not query or not limit:
        return []

    models = _models()
    hits = [
        SearchHit(
            type=entity_type,
            pk=obj.pk,
            name=obj.name,
            description=obj.description,
            thumbnail=obj.thumbnail(),
            rank=obj.search_rank,
            score=obj.search_score,
        )
        for entity_type in (types or list(EntityType))
        for obj in _search_model(models[entity_type], query, limit)
    ]
    hits.sort(key=lambda h: (h.rank, -h.score, h.name.lower()))
    return hits[:limit]
