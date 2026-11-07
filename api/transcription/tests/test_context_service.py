"""
Tests for CampaignContextService: the campaign context text that goes into Whisper prompts.
"""

from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from association.models import Association
from character.models import Character
from item.models import Artifact
from nucleus.models import GameLog
from place.models import Place
from race.models import Race
from transcription.services.CampaignContextService import CampaignContextService
from transcription.services.TranscriptionConfig import TranscriptionConfig


class FormattedContextTests(TestCase):
    def setUp(self):
        self.service = CampaignContextService(
            TranscriptionConfig(recent_threshold_days=30)
        )

    def make_log(self, days_ago):
        with patch("nucleus.models.GameLog.update_from_google"):
            return GameLog.objects.create(
                title=f"Log {days_ago}",
                url=f"log-{days_ago}",
                game_date=timezone.now() - timedelta(days=days_ago),
            )

    def test_empty_database_gives_empty_context(self):
        self.assertEqual(self.service.get_formatted_context(), "")

    def test_lists_entities_by_section(self):
        elf = Race.objects.create(name="Elf")
        Character.objects.create(name="Izar", race=elf)
        Place.objects.create(name="Hielo")
        Artifact.objects.create(name="ReDream")
        Association.objects.create(name="The Branch")

        context = self.service.get_formatted_context()

        self.assertIn("Key Characters: Izar (Elf)", context)
        self.assertIn("Important Places: Hielo", context)
        self.assertIn("Races: Elf", context)
        self.assertIn("ReDream (artifact)", context)
        self.assertIn("Organizations: The Branch", context)

    def test_recently_mentioned_characters_come_first(self):
        old = Character.objects.create(name="Aardvark")
        recent = Character.objects.create(name="Zed")
        old.logs.add(self.make_log(days_ago=400))
        recent.logs.add(self.make_log(days_ago=3))

        context = self.service.get_formatted_context()

        self.assertLess(context.index("Zed"), context.index("Aardvark"))

    def test_respects_max_length(self):
        for i in range(50):
            Character.objects.create(name=f"Character {i:02}")

        context = self.service.get_formatted_context(max_length=100)

        self.assertTrue(context)
        self.assertLessEqual(len(context), 100)

    def test_zero_max_length_gives_empty_context(self):
        Character.objects.create(name="Izar")

        self.assertEqual(self.service.get_formatted_context(max_length=0), "")
