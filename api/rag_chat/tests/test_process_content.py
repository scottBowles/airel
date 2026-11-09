from unittest.mock import patch

import httpx
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from item.models import Item
from nucleus import ai
from rag_chat.content_processors import ItemProcessor
from rag_chat.models import ContentChunk, EmbeddingRevision
from rag_chat.tasks import process_content

FIXED_VECTOR = [0.1] * 1536


def api_error():
    return ai.APIError(
        "boom", request=httpx.Request("POST", "https://api.openai.com"), body=None
    )


@patch("rag_chat.tasks.get_embedding", return_value=FIXED_VECTOR)
class ProcessContentIdempotencyTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Sword of Truth", description="A mighty blade"
        )
        self.ct = ContentType.objects.get_for_model(Item)
        self.object_id = str(self.item.pk)

    def chunks(self):
        return ContentChunk.objects.filter(content_type=self.ct, object_id=self.item.pk)

    def revision(self):
        return EmbeddingRevision.objects.get(
            content_type=self.ct, object_id=self.item.pk
        )

    def current_hash(self):
        self.item.refresh_from_db()
        return ItemProcessor().compute_source_hash(self.item)

    def test_first_call_creates_chunks_and_revision(self, mock_embed):
        result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "processed")
        self.assertGreater(self.chunks().count(), 0)
        self.assertEqual(result["chunks_created"], self.chunks().count())
        self.assertEqual(self.revision().source_hash, self.current_hash())
        self.assertTrue(mock_embed.called)

    def test_second_call_with_same_content_skips(self, mock_embed):
        process_content("item", self.object_id)
        chunk_ids = set(self.chunks().values_list("id", flat=True))
        mock_embed.reset_mock()

        result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "hash_unchanged")
        self.assertEqual(set(self.chunks().values_list("id", flat=True)), chunk_ids)
        mock_embed.assert_not_called()

    def test_changed_field_replaces_chunks_and_updates_hash(self, mock_embed):
        process_content("item", self.object_id)
        old_ids = set(self.chunks().values_list("id", flat=True))
        old_hash = self.revision().source_hash

        self.item.description = "A cursed blade"
        self.item.save()
        result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "processed")
        new_ids = set(self.chunks().values_list("id", flat=True))
        self.assertTrue(new_ids)
        self.assertFalse(old_ids & new_ids)
        self.assertIn("A cursed blade", self.chunks().first().chunk_text)
        self.assertNotEqual(self.revision().source_hash, old_hash)
        self.assertEqual(self.revision().source_hash, self.current_hash())
        self.assertEqual(EmbeddingRevision.objects.count(), 1)

    def test_force_reprocess_always_processes(self, mock_embed):
        process_content("item", self.object_id)
        old_ids = set(self.chunks().values_list("id", flat=True))
        mock_embed.reset_mock()

        result = process_content("item", self.object_id, force_reprocess=True)

        self.assertEqual(result["status"], "processed")
        mock_embed.assert_called()
        new_ids = set(self.chunks().values_list("id", flat=True))
        self.assertTrue(new_ids)
        self.assertFalse(old_ids & new_ids)
        self.assertEqual(self.revision().source_hash, self.current_hash())

    def test_existing_chunks_without_hash_are_reprocessed(self, mock_embed):
        # Rows backfilled by migration 0007 have chunks but source_hash=None.
        ContentChunk.objects.create(
            content_type=self.ct,
            object_id=self.item.pk,
            chunk_text="stale",
            chunk_index=0,
            embedding=FIXED_VECTOR,
        )
        EmbeddingRevision.objects.create(
            content_type=self.ct, object_id=self.item.pk, source_hash=None
        )

        result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "processed")
        self.assertFalse(self.chunks().filter(chunk_text="stale").exists())
        self.assertEqual(self.revision().source_hash, self.current_hash())

    def test_missing_object_returns_error(self, mock_embed):
        result = process_content("item", "999999")

        self.assertEqual(result["status"], "error")
        self.assertIn("Object not found", result["message"])
        mock_embed.assert_not_called()

    def test_partial_embedding_failure_does_not_record_hash(self, mock_embed):
        mock_embed.side_effect = [FIXED_VECTOR, api_error()]
        two_chunks = [("chunk one", {}), ("chunk two", {})]

        with patch.object(ItemProcessor, "process_content", return_value=two_chunks):
            result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "processed")
        self.assertEqual(self.chunks().count(), 1)
        self.assertFalse(
            EmbeddingRevision.objects.filter(
                content_type=self.ct, object_id=self.item.pk, source_hash__isnull=False
            ).exists()
        )

    def test_total_embedding_failure_keeps_old_chunks(self, mock_embed):
        process_content("item", self.object_id)
        old_ids = set(self.chunks().values_list("id", flat=True))

        self.item.description = "A cursed blade"
        self.item.save()
        mock_embed.side_effect = api_error()
        result = process_content("item", self.object_id)

        self.assertEqual(result["status"], "error")
        self.assertEqual(set(self.chunks().values_list("id", flat=True)), old_ids)
