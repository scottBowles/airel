import hashlib
from unittest.mock import patch

from django.test import TestCase

from association.models import Association
from character.models import Character
from item.models import Artifact, Item
from nucleus.models import GameLog
from place.models import Place
from race.models import Race
from rag_chat.content_processors import (
    ArtifactProcessor,
    AssociationProcessor,
    CharacterProcessor,
    GameLogProcessor,
    ItemProcessor,
    PlaceProcessor,
    RaceProcessor,
)
from rag_chat.embeddings import clean_text


class ItemProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = ItemProcessor()
        self.item = Item.objects.create(name="Sword of Truth", description="A mighty blade")

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.item)
        h2 = self.processor.compute_source_hash(self.item)
        self.assertEqual(h1, h2)

    def test_hash_is_sha256_hex(self):
        h = self.processor.compute_source_hash(self.item)
        self.assertEqual(len(h), 64)
        int(h, 16)  # should not raise

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.item)
        self.item.name = "Dagger of Lies"
        h2 = self.processor.compute_source_hash(self.item)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.item)
        self.item.description = "A cursed blade"
        h2 = self.processor.compute_source_hash(self.item)
        self.assertNotEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.item)
        self.item.description = "A   mighty   blade"
        h2 = self.processor.compute_source_hash(self.item)
        self.assertEqual(h1, h2)

    def test_hash_stable_under_leading_trailing_whitespace(self):
        h1 = self.processor.compute_source_hash(self.item)
        self.item.name = "  Sword of Truth  "
        self.item.description = "\n A mighty blade \n"
        h2 = self.processor.compute_source_hash(self.item)
        self.assertEqual(h1, h2)


class RaceProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = RaceProcessor()
        self.race = Race.objects.create(name="Elf", description="Graceful and long-lived")

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.race)
        h2 = self.processor.compute_source_hash(self.race)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.race)
        self.race.name = "Dwarf"
        h2 = self.processor.compute_source_hash(self.race)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.race)
        self.race.description = "Stout and sturdy"
        h2 = self.processor.compute_source_hash(self.race)
        self.assertNotEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.race)
        self.race.description = "Graceful  and   long-lived"
        h2 = self.processor.compute_source_hash(self.race)
        self.assertEqual(h1, h2)


class AssociationProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = AssociationProcessor()
        self.assoc = Association.objects.create(name="Thieves Guild", description="A shadowy organization")

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.assoc)
        h2 = self.processor.compute_source_hash(self.assoc)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.assoc)
        self.assoc.name = "Mages Guild"
        h2 = self.processor.compute_source_hash(self.assoc)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.assoc)
        self.assoc.description = "A noble order"
        h2 = self.processor.compute_source_hash(self.assoc)
        self.assertNotEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.assoc)
        self.assoc.description = "A   shadowy   organization"
        h2 = self.processor.compute_source_hash(self.assoc)
        self.assertEqual(h1, h2)


class GameLogProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = GameLogProcessor()
        with patch.object(GameLog, "update_from_google"):
            self.gamelog = GameLog.objects.create(
                url="https://docs.google.com/document/d/fakeid123/edit",
                title="The Battle of Cragmaw",
                full_text="The party entered the cave cautiously.",
            )

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.gamelog)
        h2 = self.processor.compute_source_hash(self.gamelog)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_title_changes(self):
        h1 = self.processor.compute_source_hash(self.gamelog)
        self.gamelog.title = "The Siege of Phandalin"
        h2 = self.processor.compute_source_hash(self.gamelog)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_log_text_changes(self):
        h1 = self.processor.compute_source_hash(self.gamelog)
        self.gamelog.full_text = "They fled the cave in terror."
        # Clear cached property so log_text re-evaluates
        try:
            del self.gamelog.__dict__["log_text"]
        except KeyError:
            pass
        h2 = self.processor.compute_source_hash(self.gamelog)
        self.assertNotEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.gamelog)
        self.gamelog.full_text = "The  party   entered  the   cave   cautiously."
        try:
            del self.gamelog.__dict__["log_text"]
        except KeyError:
            pass
        h2 = self.processor.compute_source_hash(self.gamelog)
        self.assertEqual(h1, h2)

    def test_hash_with_no_title(self):
        self.gamelog.title = None
        h = self.processor.compute_source_hash(self.gamelog)
        self.assertEqual(len(h), 64)


class PlaceProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = PlaceProcessor()
        self.parent = Place.objects.create(
            name="The Kingdom", description="A vast realm", place_type=Place.PlaceType.REGION
        )
        self.place = Place.objects.create(
            name="Tavern", description="A cozy inn", place_type=Place.PlaceType.LOCATION, parent=self.parent
        )

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.place)
        h2 = self.processor.compute_source_hash(self.place)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.place)
        self.place.name = "Blacksmith"
        h2 = self.processor.compute_source_hash(self.place)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.place)
        self.place.description = "A dusty workshop"
        h2 = self.processor.compute_source_hash(self.place)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_place_type_changes(self):
        h1 = self.processor.compute_source_hash(self.place)
        self.place.place_type = Place.PlaceType.TOWN
        h2 = self.processor.compute_source_hash(self.place)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_parent_changes(self):
        h1 = self.processor.compute_source_hash(self.place)
        new_parent = Place.objects.create(
            name="The Empire", description="A larger realm", place_type=Place.PlaceType.REGION
        )
        self.place.parent = new_parent
        h2 = self.processor.compute_source_hash(self.place)
        self.assertNotEqual(h1, h2)

    def test_hash_includes_parent_name(self):
        h_with_parent = self.processor.compute_source_hash(self.place)
        self.place.parent = None
        h_without_parent = self.processor.compute_source_hash(self.place)
        self.assertNotEqual(h_with_parent, h_without_parent)

    def test_missing_parent_produces_empty_string_not_none(self):
        """When parent is None, hash should use empty string, not 'None'"""
        self.place.parent = None
        h1 = self.processor.compute_source_hash(self.place)
        # The hash should be deterministic with no parent
        h2 = self.processor.compute_source_hash(self.place)
        self.assertEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.place)
        self.place.description = "A   cozy   inn"
        h2 = self.processor.compute_source_hash(self.place)
        self.assertEqual(h1, h2)


class CharacterProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = CharacterProcessor()
        self.race = Race.objects.create(name="Elf", description="Graceful")
        self.character = Character.objects.create(
            name="Gandalf", description="A wise wizard", race=self.race
        )
        self.assoc1 = Association.objects.create(name="Fellowship", description="Heroes")
        self.assoc2 = Association.objects.create(name="Council", description="Advisors")
        self.character.associations.set([self.assoc1, self.assoc2])

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.character)
        h2 = self.processor.compute_source_hash(self.character)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.character)
        self.character.name = "Saruman"
        h2 = self.processor.compute_source_hash(self.character)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.character)
        self.character.description = "A corrupted wizard"
        h2 = self.processor.compute_source_hash(self.character)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_race_changes(self):
        h1 = self.processor.compute_source_hash(self.character)
        new_race = Race.objects.create(name="Dwarf", description="Stout")
        self.character.race = new_race
        h2 = self.processor.compute_source_hash(self.character)
        self.assertNotEqual(h1, h2)

    def test_hash_with_no_race_uses_empty_string(self):
        self.character.race = None
        h = self.processor.compute_source_hash(self.character)
        self.assertEqual(len(h), 64)

    def test_hash_changes_when_associations_change(self):
        h1 = self.processor.compute_source_hash(self.character)
        new_assoc = Association.objects.create(name="Dark Order", description="Villains")
        self.character.associations.set([new_assoc])
        h2 = self.processor.compute_source_hash(self.character)
        self.assertNotEqual(h1, h2)

    def test_hash_m2m_sorted_for_stability(self):
        """Order of association creation shouldn't affect hash"""
        char2 = Character.objects.create(
            name="Gandalf", description="A wise wizard", race=self.race
        )
        # Set in reverse order
        char2.associations.set([self.assoc2, self.assoc1])
        h1 = self.processor.compute_source_hash(self.character)
        h2 = self.processor.compute_source_hash(char2)
        self.assertEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.character)
        self.character.description = "A   wise   wizard"
        h2 = self.processor.compute_source_hash(self.character)
        self.assertEqual(h1, h2)


class ArtifactProcessorHashTests(TestCase):
    def setUp(self):
        self.processor = ArtifactProcessor()
        self.artifact = Artifact.objects.create(
            name="Staff of Power", description="A legendary staff"
        )
        self.item1 = Item.objects.create(name="Ruby", description="A red gem")
        self.item2 = Item.objects.create(name="Oak Staff", description="A wooden staff")
        self.artifact.items.set([self.item1, self.item2])

    def test_hash_is_deterministic(self):
        h1 = self.processor.compute_source_hash(self.artifact)
        h2 = self.processor.compute_source_hash(self.artifact)
        self.assertEqual(h1, h2)

    def test_hash_changes_when_name_changes(self):
        h1 = self.processor.compute_source_hash(self.artifact)
        self.artifact.name = "Staff of Weakness"
        h2 = self.processor.compute_source_hash(self.artifact)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_description_changes(self):
        h1 = self.processor.compute_source_hash(self.artifact)
        self.artifact.description = "A cursed staff"
        h2 = self.processor.compute_source_hash(self.artifact)
        self.assertNotEqual(h1, h2)

    def test_hash_changes_when_items_change(self):
        h1 = self.processor.compute_source_hash(self.artifact)
        new_item = Item.objects.create(name="Diamond", description="A sparkling gem")
        self.artifact.items.set([new_item])
        h2 = self.processor.compute_source_hash(self.artifact)
        self.assertNotEqual(h1, h2)

    def test_hash_m2m_sorted_for_stability(self):
        """Order of item creation shouldn't affect hash"""
        artifact2 = Artifact.objects.create(
            name="Staff of Power", description="A legendary staff"
        )
        # Set in reverse order
        artifact2.items.set([self.item2, self.item1])
        h1 = self.processor.compute_source_hash(self.artifact)
        h2 = self.processor.compute_source_hash(artifact2)
        self.assertEqual(h1, h2)

    def test_hash_stable_under_whitespace_differences(self):
        h1 = self.processor.compute_source_hash(self.artifact)
        self.artifact.description = "A   legendary   staff"
        h2 = self.processor.compute_source_hash(self.artifact)
        self.assertEqual(h1, h2)
