"""
GraphQL tests for associations, through the /graphql/ endpoint the frontend uses.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from gqlauth.jwt.types_ import ObtainJSONWebTokenType
from strawberry.relay import to_base64

from .models import Association

PAYLOAD = """
fragment Payload on Association { __typename id name }
"""


class AssociationGraphQLTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create(username="staff", is_staff=True)
        self.player = User.objects.create(username="player")

    def graphql(self, query, variables=None, user=None):
        headers = {}
        if user:
            # Same token googleLogin issues; the web client sends it like this
            token = ObtainJSONWebTokenType.from_user(user).token.token
            headers["Authorization"] = f"JWT {token}"
        response = self.client.post(
            "/graphql/",
            json.dumps(
                {
                    "query": query + (PAYLOAD if "...Payload" in query else ""),
                    "variables": variables or {},
                }
            ),
            content_type="application/json",
            headers=headers,
        )
        return response.json()

    def assertRefused(self, result, field):
        """Refusals come back as an OperationInfo payload or a GraphQL error."""
        payload = (result.get("data") or {}).get(field)
        if payload is None:
            self.assertIn("errors", result)
        else:
            self.assertEqual(payload["__typename"], "OperationInfo")

    def test_list_associations(self):
        Association.objects.create(name="The Branch")
        Association.objects.create(name="Void Spiders")

        result = self.graphql(
            "{ associations { edges { node { id name } } } }", user=self.player
        )

        self.assertNotIn("errors", result)
        names = {e["node"]["name"] for e in result["data"]["associations"]["edges"]}
        self.assertEqual(names, {"The Branch", "Void Spiders"})

    def test_staff_can_create_association(self):
        result = self.graphql(
            """
            mutation Create($input: AssociationInput!) {
                createAssociation(input: $input) { ...Payload }
            }
            """,
            {"input": {"name": "The Branch", "description": "Inventors of AI"}},
            user=self.staff,
        )

        self.assertEqual(result["data"]["createAssociation"]["name"], "The Branch")
        self.assertEqual(
            Association.objects.get(name="The Branch").description, "Inventors of AI"
        )

    def test_non_staff_cannot_create_association(self):
        result = self.graphql(
            """
            mutation Create($input: AssociationInput!) {
                createAssociation(input: $input) { ...Payload }
            }
            """,
            {"input": {"name": "The Branch"}},
            user=self.player,
        )

        self.assertRefused(result, "createAssociation")
        self.assertFalse(Association.objects.exists())

    def update(self, association, name, user):
        return self.graphql(
            """
            mutation Update($input: AssociationInputPartial!) {
                updateAssociation(input: $input) { ...Payload }
            }
            """,
            {"input": {"id": to_base64("Association", association.pk), "name": name}},
            user=user,
        )

    def test_update_renames_and_releases_lock(self):
        association = Association.objects.create(name="Old name")
        association.lock(self.staff)

        result = self.update(association, "New name", self.staff)

        self.assertEqual(result["data"]["updateAssociation"]["name"], "New name")
        association.refresh_from_db()
        self.assertEqual(association.name, "New name")
        self.assertIsNone(association.lock_user)

    def test_update_refused_when_locked_by_someone_else(self):
        other_staff = get_user_model().objects.create(username="other", is_staff=True)
        association = Association.objects.create(name="Old name")
        association.lock(other_staff)

        result = self.update(association, "New name", self.staff)

        self.assertRefused(result, "updateAssociation")
        association.refresh_from_db()
        self.assertEqual(association.name, "Old name")
