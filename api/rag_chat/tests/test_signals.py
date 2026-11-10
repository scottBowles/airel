from datetime import datetime, timezone
from unittest.mock import call, patch

from django.db.models.signals import m2m_changed, post_save
from django.test import TestCase

from association.models import Association
from character.models import Character
from item.models import Artifact, Item
from nucleus.models import GameLog
from place.models import Place
from race.models import Race
from rag_chat.signals import disconnect_embedding_signals


def make_gamelog(n=1):
    # bulk_create skips GameLog.save(), which fetches from Google Drive.
    (log,) = GameLog.objects.bulk_create(
        [
            GameLog(
                url=f"https://test.invalid/logs/{n}",
                google_id=f"test-log-{n}",
                title=f"Session {n}",
                game_date=datetime(2026, 1, n, tzinfo=timezone.utc),
            )
        ]
    )
    return log


@patch("rag_chat.signals.process_content.delay")
class EmbeddingSignalTests(TestCase):
    def test_post_save_queues_each_tracked_model(self, delay):
        cases = [
            (Character, "character"),
            (Place, "place"),
            (Item, "item"),
            (Artifact, "artifact"),
            (Race, "race"),
            (Association, "association"),
        ]
        for model, content_type in cases:
            with self.subTest(model=model.__name__):
                delay.reset_mock()
                with self.captureOnCommitCallbacks(execute=True):
                    obj = model.objects.create(name=f"A {content_type}")
                delay.assert_called_once_with(content_type, str(obj.pk))

    def test_gamelog_save_queues_gamelog(self, delay):
        log = make_gamelog()
        with self.captureOnCommitCallbacks(execute=True):
            log.title = "Renamed"
            log.save()
        delay.assert_called_once_with("gamelog", str(log.pk))

    def test_queues_only_after_commit(self, delay):
        with self.captureOnCommitCallbacks() as callbacks:
            Item.objects.create(name="Lamp")
            delay.assert_not_called()
        self.assertEqual(len(callbacks), 1)

    def test_untracked_model_does_not_queue(self, delay):
        from nucleus.models import Alias

        with self.captureOnCommitCallbacks(execute=True):
            Alias.objects.create(name="Someone")
        delay.assert_not_called()

    def test_broker_error_does_not_break_save(self, delay):
        delay.side_effect = ConnectionError("redis down")
        with self.assertLogs("rag_chat.signals", "ERROR"):
            with self.captureOnCommitCallbacks(execute=True):
                Item.objects.create(name="Lamp")


@patch("rag_chat.signals.process_content.delay")
class EmbeddingM2MSignalTests(TestCase):
    def setUp(self):
        with disconnect_embedding_signals():
            self.character = Character.objects.create(name="Ilsa")
            self.association = Association.objects.create(name="Crew")
            self.place = Place.objects.create(name="Port Veil")
            self.artifact = Artifact.objects.create(name="Lantern Heart")
            self.item = Item.objects.create(name="Compass")
            self.log = make_gamelog()

    def assert_queued(self, delay, content_type, obj):
        delay.assert_called_once_with(content_type, str(obj.pk))
        delay.reset_mock()

    def test_add_remove_clear_each_queue_once(self, delay):
        relations = [
            (self.character, "associations", self.association, "character"),
            (self.log, "places_set_in", self.place, "gamelog"),
            (self.artifact, "items", self.item, "artifact"),
        ]
        for owner, field, other, content_type in relations:
            with self.subTest(field=field):
                manager = getattr(owner, field)
                with self.captureOnCommitCallbacks(execute=True):
                    manager.add(other)
                self.assert_queued(delay, content_type, owner)
                with self.captureOnCommitCallbacks(execute=True):
                    manager.remove(other)
                self.assert_queued(delay, content_type, owner)
                manager.add(other)
                delay.reset_mock()
                with self.captureOnCommitCallbacks(execute=True):
                    manager.clear()
                self.assert_queued(delay, content_type, owner)

    def test_reverse_add_queues_the_owning_side(self, delay):
        other = Character.objects.create(name="Teo")
        delay.reset_mock()
        with self.captureOnCommitCallbacks(execute=True):
            self.association.characters.add(self.character, other)
        self.assertCountEqual(
            delay.call_args_list,
            [
                call("character", str(self.character.pk)),
                call("character", str(other.pk)),
            ],
        )

    def test_untracked_m2m_does_not_queue(self, delay):
        with self.captureOnCommitCallbacks(execute=True):
            self.character.related_items.add(self.item)
        delay.assert_not_called()


@patch("rag_chat.signals.process_content.delay")
class DisconnectEmbeddingSignalsTests(TestCase):
    def test_suppresses_saves_and_m2m_changes(self, delay):
        with self.captureOnCommitCallbacks(execute=True):
            with disconnect_embedding_signals():
                character = Character.objects.create(name="Ilsa")
                character.associations.add(Association.objects.create(name="Crew"))
        delay.assert_not_called()

    def test_reconnects_on_exit_even_after_error(self, delay):
        with self.assertRaises(RuntimeError):
            with disconnect_embedding_signals():
                raise RuntimeError
        self.assertTrue(post_save.has_listeners(Item))
        self.assertTrue(m2m_changed.has_listeners(Character.associations.through))
        with self.captureOnCommitCallbacks(execute=True):
            item = Item.objects.create(name="Lamp")
        delay.assert_called_once_with("item", str(item.pk))

    def test_nested_blocks_stay_disconnected_until_outermost_exit(self, delay):
        with disconnect_embedding_signals():
            with disconnect_embedding_signals():
                pass
            with self.captureOnCommitCallbacks(execute=True):
                Item.objects.create(name="Lamp")
            delay.assert_not_called()
        with self.captureOnCommitCallbacks(execute=True):
            item = Item.objects.create(name="Rope")
        delay.assert_called_once_with("item", str(item.pk))
