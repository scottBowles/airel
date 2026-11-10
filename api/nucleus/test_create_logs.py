from datetime import datetime, timezone
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from nucleus.models import GameLog

CREATED = "2026-01-05T12:00:00.000Z"


def drive_file(n):
    return {
        "id": f"drive-{n}",
        "name": f"2026-01-0{n} Session {n}",
        "webViewLink": f"https://docs.google.com/document/d/drive-{n}/edit",
        "createdTime": CREATED,
    }


def fake_fetch_airel_file(google_id):
    n = google_id.removeprefix("drive-")
    return drive_file(int(n))


# Every Google Drive call create_logs can reach is mocked.
@patch("nucleus.gdrive.fetch_airel_file_text", return_value="Log text")
@patch("nucleus.gdrive.fetch_airel_file", side_effect=fake_fetch_airel_file)
@patch("nucleus.management.commands.create_logs.fetch_all_airel_logs")
@patch("rag_chat.signals.process_content.delay")
@patch("nucleus.management.commands.create_logs.process_all_content.delay")
class CreateLogsCommandTests(TestCase):
    def run_command(self, **kwargs):
        with self.captureOnCommitCallbacks(execute=True):
            call_command("create_logs", stdout=StringIO(), **kwargs)

    def assert_signals_connected(self, per_save_delay):
        per_save_delay.reset_mock()
        log = GameLog.objects.first()
        with self.captureOnCommitCallbacks(execute=True):
            log.title = "Renamed"
            log.save()
        per_save_delay.assert_called_once_with("gamelog", str(log.pk))

    def test_imports_logs_without_per_save_embedding(
        self, batch_delay, per_save_delay, fetch_logs, *_
    ):
        # One existing log (updated by the command) and two new ones.
        GameLog.objects.bulk_create(
            [
                GameLog(
                    url=drive_file(1)["webViewLink"],
                    google_id="drive-1",
                    title="2026-01-01 Session 1",
                    game_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
            ]
        )
        fetch_logs.return_value = [drive_file(1), drive_file(2), drive_file(3)]

        self.run_command()

        self.assertEqual(GameLog.objects.count(), 3)
        per_save_delay.assert_not_called()
        batch_delay.assert_called_once_with(
            content_types=["gamelog"], force_reprocess=False
        )

    def test_signals_reconnected_after_command(
        self, batch_delay, per_save_delay, fetch_logs, *_
    ):
        fetch_logs.return_value = [drive_file(1)]
        self.run_command()
        self.assert_signals_connected(per_save_delay)

    def test_interrupted_import_reconnects_and_skips_batch(
        self, batch_delay, per_save_delay, fetch_logs, fetch_file, _
    ):
        fetch_logs.return_value = [drive_file(1), drive_file(2)]
        fetch_file.side_effect = [drive_file(1), RuntimeError("Drive is down")]

        with self.assertRaises(RuntimeError):
            self.run_command()

        batch_delay.assert_not_called()
        per_save_delay.assert_not_called()
        # The first log was saved before the failure; signals are back on regardless.
        self.assertEqual(GameLog.objects.count(), 1)
        self.assert_signals_connected(per_save_delay)

    def test_broker_outage_warns_instead_of_failing(
        self, batch_delay, per_save_delay, fetch_logs, *_
    ):
        fetch_logs.return_value = [drive_file(1)]
        batch_delay.side_effect = ConnectionError("Redis is down")

        stderr = StringIO()
        self.run_command(stderr=stderr)

        self.assertEqual(GameLog.objects.count(), 1)
        self.assertIn("process_game_logs --types gamelog", stderr.getvalue())
