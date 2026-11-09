"""The `search` query (nucleus/search.py), through the /graphql/ endpoint the web app uses."""

import json

from django.test import TestCase
from strawberry.relay import to_base64

from association.models import Association
from character.models import Character
from item.models import Artifact, Item
from nucleus.models import Alias
from place.models import Place
from race.models import Race

SEARCH = """
query Search($query: String!, $types: [EntityType!], $limit: Int) {
    search(query: $query, types: $types, limit: $limit) {
        id name type description thumbnail
    }
}
"""


class SearchQueryTests(TestCase):
    def search(self, query, **variables):
        response = self.client.post(
            "/graphql/",
            json.dumps({"query": SEARCH, "variables": {"query": query, **variables}}),
            content_type="application/json",
        )
        result = response.json()
        self.assertNotIn("errors", result)
        return result["data"]["search"]

    def names(self, query, **variables):
        return [hit["name"] for hit in self.search(query, **variables)]

    def test_hit_fields(self):
        place = Place.objects.create(
            name="Port Veil",
            description="A floating harbour town.",
            image_ids=["img-1", "img-2"],
        )

        [hit] = self.search("Port Veil")

        self.assertEqual(
            hit,
            {
                "id": to_base64("Place", place.pk),
                "name": "Port Veil",
                "type": "PLACE",
                "description": "A floating harbour town.",
                "thumbnail": "img-1",
            },
        )

    def test_covers_all_six_types(self):
        for model in (Artifact, Association, Character, Item, Place, Race):
            model.objects.create(name=f"Ember {model.__name__}")

        types = {hit["type"] for hit in self.search("ember")}

        self.assertEqual(
            types, {"ARTIFACT", "ASSOCIATION", "CHARACTER", "ITEM", "PLACE", "RACE"}
        )

    def test_partial_name(self):
        Place.objects.create(name="Port Veil")
        Place.objects.create(name="Calder")

        self.assertEqual(self.names("veil"), ["Port Veil"])
        self.assertEqual(self.names("port v"), ["Port Veil"])

    def test_typos(self):
        Character.objects.create(name="Siraen")
        Place.objects.create(name="Port Veil")
        Item.objects.create(name="Tide Compass")

        self.assertEqual(self.names("Siren"), ["Siraen"])
        self.assertEqual(self.names("Port Veel"), ["Port Veil"])
        self.assertEqual(self.names("compas"), ["Tide Compass"])

    def test_unrelated_query_finds_nothing(self):
        Character.objects.create(name="Siraen")
        Item.objects.create(name="Signal Flare")

        # Shares only its first two letters with "Signal".
        self.assertEqual(self.names("Siren"), ["Siraen"])

        self.assertEqual(self.names("zzzz"), [])
        self.assertEqual(self.names("   "), [])

    def test_matches_aliases(self):
        teo = Character.objects.create(name="Teo Vance")
        teo.aliases.add(Alias.objects.create(name="The Fixer"))

        self.assertEqual(self.names("fixer"), ["Teo Vance"])
        self.assertEqual(self.names("Fixxer"), ["Teo Vance"])

    def test_ranks_exact_then_prefix_then_contains_then_similar(self):
        Item.objects.create(name="Lantern Oil")  # prefix
        Place.objects.create(name="The Drowned Lantern")  # contains
        Item.objects.create(name="Lantrn")  # similar only
        Artifact.objects.create(name="Lantern")  # exact

        self.assertEqual(
            self.names("lantern"),
            ["Lantern", "Lantern Oil", "The Drowned Lantern", "Lantrn"],
        )

    def test_exact_alias_beats_prefix_name(self):
        Character.objects.create(name="Marrowind")  # name prefix
        ilsa = Character.objects.create(name="Captain Ilsa Marrow")
        ilsa.aliases.add(Alias.objects.create(name="Marrow"))  # exact alias

        self.assertEqual(self.names("marrow"), ["Captain Ilsa Marrow", "Marrowind"])

    def test_types_filter(self):
        Character.objects.create(name="Ember Vance")
        Association.objects.create(name="Ember Syndicate")
        Place.objects.create(name="Ember Reach")

        hits = self.search("ember", types=["ASSOCIATION", "PLACE"])

        self.assertEqual(
            {(h["type"], h["name"]) for h in hits},
            {("ASSOCIATION", "Ember Syndicate"), ("PLACE", "Ember Reach")},
        )

    def test_limit(self):
        for i in range(8):
            Item.objects.create(name=f"Signal Flare {i}")
        Race.objects.create(name="Signal")

        self.assertEqual(len(self.search("signal", limit=3)), 3)
        # The limit is over all types together, after ranking: the exact match survives.
        self.assertEqual(self.names("signal", limit=1), ["Signal"])
        # Default and cap.
        self.assertEqual(len(self.search("signal")), 9)
        self.assertEqual(len(self.search("signal", limit=1000)), 9)
        self.assertEqual(self.search("signal", limit=0), [])
