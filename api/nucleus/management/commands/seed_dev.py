"""Seed a development database with sign-in users and a small campaign world.

Development only (refuses when DEBUG is off). Safe to rerun: every row is looked up by a
fixed key before it is created. Users are always ensured. The world (places, characters,
logs and so on) is skipped when the database already holds game logs that aren't seed
logs, such as a copy of production, unless --world is passed.
"""

from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from association.models import Association
from character.models import Character
from item.models import Artifact, Item
from nucleus.models import Alias, GameLog
from place.models import Place
from race.models import Race
from rag_chat.signals import disconnect_embedding_signals

SEED_LOG_URL_PREFIX = "https://seed.airel.invalid/logs/"

# username -> flags. Sign in as one with `manage.py dev_login <username>`.
USERS = {
    "dm": {"is_staff": True, "is_superuser": True, "isDM": True, "first_name": "Dana"},
    "player": {"first_name": "Pat", "pc_name": "Wren Ashdown"},
}

RACES = [
    ("Human", "Adaptable and ambitious, found in every port of the Reach."),
    ("Vashari", "Tall, silver-eyed spacefarers who navigate by starsong."),
]

ASSOCIATIONS = [
    ("Kontularien Crew", "The crew of the salvage ship Kontularien."),
    ("Ember Syndicate", "A smuggling cartel that runs the Cinder Belt."),
]

# (name, place_type, parent name, description)
PLACES = [
    ("Ostra", "Star", None, "A dim orange star at the edge of the Reach."),
    ("Calder", "Planet", "Ostra", "A storm-wrapped ocean world."),
    ("Port Veil", "Town", "Calder", "A floating harbour town built on old platforms."),
    ("The Drowned Lantern", "Location", "Port Veil", "A tavern below the waterline."),
]

# (name, race, association, description)
CHARACTERS = [
    ("Captain Ilsa Marrow", "Human", "Kontularien Crew", "Captain of the Kontularien."),
    ("Teo Vance", "Human", "Ember Syndicate", "A fixer with debts everywhere."),
    ("Siraen", "Vashari", "Kontularien Crew", "The ship's navigator."),
]

ITEMS = [
    ("Tide Compass", "A compass that points toward the nearest open water."),
    ("Signal Flare", "A single-use flare that burns blue for an hour."),
]

ARTIFACTS = [
    ("The Lantern Heart", "A glowing core said to power the first drowned city."),
]

# (session number, title, game date, brief, places, characters)
LOGS = [
    (
        1,
        "Session 1: Arrival at Port Veil",
        datetime(2026, 1, 10, tzinfo=timezone.utc),
        "The crew docks at Port Veil and meets Teo Vance at the Drowned Lantern.",
        ["Port Veil", "The Drowned Lantern"],
        ["Captain Ilsa Marrow", "Teo Vance", "Siraen"],
    ),
    (
        2,
        "Session 2: The Tide Compass",
        datetime(2026, 1, 24, tzinfo=timezone.utc),
        "Teo offers the Tide Compass in exchange for passage off Calder.",
        ["Calder"],
        ["Captain Ilsa Marrow", "Teo Vance"],
    ),
    (
        3,
        "Session 3: Into the Deep",
        datetime(2026, 2, 7, tzinfo=timezone.utc),
        "Siraen follows the compass to the ruins that hold the Lantern Heart.",
        ["Calder"],
        ["Siraen"],
    ),
]


class Command(BaseCommand):
    help = "Seed a development database with sign-in users and a small campaign world."

    def add_arguments(self, parser):
        parser.add_argument(
            "--world",
            action="store_true",
            help="Add the seed world even when the database already has other game logs.",
        )

    def handle(self, *args, world=False, **options):
        if not settings.DEBUG:
            raise CommandError("seed_dev only runs with DEBUG on (development).")

        # The embedding signals would queue a process_content task per saved row.
        with disconnect_embedding_signals(), transaction.atomic():
            self.seed_users()
            other_logs = GameLog.objects.exclude(url__startswith=SEED_LOG_URL_PREFIX)
            if other_logs.exists() and not world:
                self.stdout.write(
                    "Skipped the seed world: this database already has game logs. "
                    "Pass --world to add it anyway."
                )
            else:
                self.seed_world()

        self.stdout.write(self.style.SUCCESS("Seed data ready."))

    def seed_users(self):
        User = get_user_model()
        for username, fields in USERS.items():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@seed.airel.invalid", **fields},
            )
            if created:
                user.set_unusable_password()
                user.save()
            self.stdout.write(f"User {username}: {'created' if created else 'exists'}")

    def seed_world(self):
        races = {
            name: self.entity(Race, name, description) for name, description in RACES
        }
        associations = {
            name: self.entity(Association, name, description)
            for name, description in ASSOCIATIONS
        }

        places = {}
        for name, place_type, parent, description in PLACES:
            places[name] = self.entity(
                Place,
                name,
                description,
                place_type=place_type,
                parent=places.get(parent),
            )

        characters = {}
        for name, race, association, description in CHARACTERS:
            character = self.entity(Character, name, description, race=races[race])
            character.associations.add(associations[association])
            characters[name] = character

        items = {name: self.entity(Item, name, d) for name, d in ITEMS}
        for name, description in ARTIFACTS:
            artifact = self.entity(Artifact, name, description)
            artifact.related_places.add(places["Calder"])

        characters["Teo Vance"].related_items.add(items["Tide Compass"])

        previous = None
        for number, title, game_date, brief, log_places, log_characters in LOGS:
            log = self.game_log(number, title, game_date, brief, previous)
            log.places_set_in.add(*(places[name] for name in log_places))
            for name in log_characters:
                characters[name].logs.add(log)
            previous = log

        self.stdout.write(
            f"World: {len(races)} races, {len(associations)} associations, "
            f"{len(places)} places, {len(characters)} characters, {len(items)} items, "
            f"{len(ARTIFACTS)} artifacts, {len(LOGS)} game logs"
        )

    def entity(self, model, name, description, **fields):
        obj, created = model.objects.get_or_create(
            name=name, defaults={"description": description, **fields}
        )
        if created:
            obj.aliases.add(Alias.objects.create(name=name, is_primary=True))
        return obj

    def game_log(self, number, title, game_date, brief, previous):
        url = f"{SEED_LOG_URL_PREFIX}{number}"
        log = GameLog.objects.filter(url=url).first()
        if log:
            return log
        # bulk_create skips GameLog.save(), which would fetch the log from Google Drive.
        (log,) = GameLog.objects.bulk_create(
            [
                GameLog(
                    url=url,
                    google_id=f"seed-log-{number}",
                    title=title,
                    session_number=number,
                    game_date=game_date,
                    google_created_time=game_date,
                    brief=brief,
                    synopsis=brief,
                    full_text=f"{title}\n\n{brief}",
                    last_game_log=previous,
                )
            ]
        )
        return log
