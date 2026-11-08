"""Issue sign-in tokens for a user, so an agent can use the web app without Google.

Development only (refuses when DEBUG is off). The web app reads two cookies, access_token
and refresh_token; set them in the browser on the web app's origin and reload. The
access token lasts 5 minutes, and the web app renews it from the refresh token.

    manage.py dev_login            # the seed DM (see seed_dev)
    manage.py dev_login player     # any existing username
    manage.py dev_login --json     # {"access_token": ..., "refresh_token": ...}
"""

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from gqlauth.jwt.types_ import ObtainJSONWebTokenType


class Command(BaseCommand):
    help = "Print sign-in tokens for a user (development only)."

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?", default="dm")
        parser.add_argument("--json", action="store_true", help="Print JSON only.")

    def handle(self, *args, username, **options):
        if not settings.DEBUG:
            raise CommandError("dev_login only runs with DEBUG on (development).")

        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            raise CommandError(
                f"No user {username!r}. Run `manage.py seed_dev` to create dm and player."
            )

        result = ObtainJSONWebTokenType.from_user(user)
        tokens = {
            "access_token": result.token.token,
            "refresh_token": result.refresh_token.token,
        }
        if options["json"]:
            self.stdout.write(json.dumps(tokens))
            return

        self.stdout.write(f"Tokens for {username} (staff: {user.is_staff}):")
        for name, value in tokens.items():
            self.stdout.write(f"{name}={value}")
