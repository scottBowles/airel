import numpy as np
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from character.tests.factories import NPCFactory
from rag_chat.models import ContentChunk, EmbeddingRevision
from rag_chat.tasks import cleanup_orphaned_chunks


class CleanupOrphanedChunksTests(TestCase):
    def _make_chunk(self, content_type, object_id, chunk_index=0):
        return ContentChunk.objects.create(
            content_type=content_type,
            object_id=object_id,
            chunk_text="test chunk",
            chunk_index=chunk_index,
            embedding=np.zeros(1536).tolist(),
        )

    def _make_revision(self, content_type, object_id):
        return EmbeddingRevision.objects.create(
            content_type=content_type,
            object_id=object_id,
            source_hash=None,
        )

    def test_deletes_orphaned_chunks_and_revisions(self):
        character = NPCFactory()
        ct = ContentType.objects.get_for_model(character)

        # Create chunks and revisions for the real character
        self._make_chunk(ct, character.id)
        self._make_revision(ct, character.id)

        # Create chunks and revisions for a non-existent object
        orphaned_id = 999999
        self._make_chunk(ct, orphaned_id)
        self._make_revision(ct, orphaned_id)

        self.assertEqual(ContentChunk.objects.count(), 2)
        self.assertEqual(EmbeddingRevision.objects.count(), 2)

        result = cleanup_orphaned_chunks()

        self.assertEqual(result["orphaned_chunks_deleted"], 1)
        self.assertEqual(result["orphaned_revisions_deleted"], 1)

        # Valid objects remain
        self.assertEqual(ContentChunk.objects.filter(object_id=character.id).count(), 1)
        self.assertEqual(
            EmbeddingRevision.objects.filter(object_id=character.id).count(), 1
        )

        # Orphaned objects removed
        self.assertFalse(ContentChunk.objects.filter(object_id=orphaned_id).exists())
        self.assertFalse(
            EmbeddingRevision.objects.filter(object_id=orphaned_id).exists()
        )

    def test_keeps_revisions_when_no_orphans(self):
        character = NPCFactory()
        ct = ContentType.objects.get_for_model(character)

        self._make_chunk(ct, character.id)
        self._make_revision(ct, character.id)

        result = cleanup_orphaned_chunks()

        self.assertEqual(result["orphaned_chunks_deleted"], 0)
        self.assertEqual(result["orphaned_revisions_deleted"], 0)
        self.assertEqual(ContentChunk.objects.count(), 1)
        self.assertEqual(EmbeddingRevision.objects.count(), 1)

    def test_revision_without_chunk_not_cleaned(self):
        """EmbeddingRevision cleanup is keyed off chunk object_ids, so a
        revision with no matching chunk won't be found by the current logic."""
        character = NPCFactory()
        ct = ContentType.objects.get_for_model(character)

        # Only a revision, no chunk
        self._make_revision(ct, character.id)

        result = cleanup_orphaned_chunks()

        # No chunks existed so nothing scanned — revision remains
        self.assertEqual(EmbeddingRevision.objects.count(), 1)
