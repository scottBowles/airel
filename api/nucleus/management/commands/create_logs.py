from django.core.management.base import BaseCommand
from tqdm import tqdm

from nucleus.gdrive import fetch_all_airel_logs
from nucleus.models import GameLog
from rag_chat.signals import disconnect_embedding_signals
from rag_chat.tasks import process_all_content

CATCH_UP_COMMAND = "python manage.py process_game_logs --types gamelog"


class Command(BaseCommand):
    help = "Create GameLog objects from google drive and update existing ones"

    def handle(self, *args, **options):
        log_files = fetch_all_airel_logs()

        # Embedding signals are disconnected for the import: every saved GameLog would
        # otherwise queue its own process_content task, flooding the Celery queue with
        # one task per log. Instead, a single process_all_content batch is queued
        # automatically once the loop finishes (below), which re-embeds only the logs
        # whose content changed.
        #
        # If this command is interrupted (Ctrl-C, a Drive error), that batch is never
        # queued and the logs saved so far are not embedded. Catch up manually with:
        #     python manage.py process_game_logs --types gamelog
        with disconnect_embedding_signals():
            for log_file in tqdm(log_files):
                log, created = GameLog.objects.get_or_create(
                    url=log_file["webViewLink"]
                )
                if not created:
                    log.update_from_google_file_info(log_file)
                    log.save()

        try:
            process_all_content.delay(content_types=["gamelog"], force_reprocess=False)
        except Exception as e:
            self.stderr.write(
                self.style.WARNING(
                    f"Could not queue re-embedding ({e}). Run `{CATCH_UP_COMMAND}`."
                )
            )
            return
        self.stdout.write(
            self.style.SUCCESS("Queued re-embedding of game logs (process_all_content).")
        )
