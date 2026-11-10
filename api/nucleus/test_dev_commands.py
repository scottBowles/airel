import json
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from gqlauth.jwt.types_ import TokenType

from character.models import Character
from nucleus.models import GameLog
from place.models import Place


def run(*args):
    out = StringIO()
    call_command(*args, stdout=out)
    return out.getvalue()


@override_settings(DEBUG=True)
class SeedDevTests(TestCase):
    def test_seeds_users_and_world_and_is_idempotent(self):
        run("seed_dev")
        counts = (
            GameLog.objects.count(),
            Character.objects.count(),
            Place.objects.count(),
        )
        run("seed_dev")

        self.assertEqual(
            counts,
            (GameLog.objects.count(), Character.objects.count(), Place.objects.count()),
        )
        self.assertEqual(counts, (3, 3, 4))
        dm = get_user_model().objects.get(username="dm")
        self.assertTrue(dm.is_staff and dm.is_superuser)
        self.assertFalse(dm.has_usable_password())
        logs = GameLog.objects.order_by("session_number")
        self.assertEqual(logs[2].last_game_log, logs[1])
        self.assertEqual(Place.objects.get(name="Port Veil").parent.name, "Calder")

    @patch("rag_chat.signals.process_content.delay")
    def test_queues_no_embedding_tasks(self, delay):
        with self.captureOnCommitCallbacks(execute=True):
            run("seed_dev")
        self.assertTrue(Character.objects.exists())
        delay.assert_not_called()

    def test_skips_world_when_database_has_other_logs(self):
        GameLog.objects.bulk_create([GameLog(url="https://docs.example/real-log")])

        out = run("seed_dev")

        self.assertIn("Skipped the seed world", out)
        self.assertEqual(Character.objects.count(), 0)
        self.assertTrue(get_user_model().objects.filter(username="player").exists())

        run("seed_dev", "--world")
        self.assertEqual(Character.objects.count(), 3)

    @override_settings(DEBUG=False)
    def test_refuses_without_debug(self):
        with self.assertRaises(CommandError):
            run("seed_dev")


@override_settings(DEBUG=True)
class DevLoginTests(TestCase):
    def test_prints_tokens_for_the_user(self):
        run("seed_dev")

        tokens = json.loads(run("dev_login", "player", "--json"))

        user = TokenType.from_token(tokens["access_token"]).get_user_instance()
        self.assertEqual(user.username, "player")
        self.assertTrue(tokens["refresh_token"])

    def test_unknown_user_is_an_error(self):
        with self.assertRaises(CommandError):
            run("dev_login", "nobody")

    @override_settings(DEBUG=False)
    def test_refuses_without_debug(self):
        with self.assertRaises(CommandError):
            run("dev_login")
