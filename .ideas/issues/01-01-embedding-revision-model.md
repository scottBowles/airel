# Issue 01-01: Add `EmbeddingRevision` model

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** None
**Blocks:** 01-02, 01-03

## Summary

Add a new `EmbeddingRevision` model to `rag_chat/models.py` that tracks whether a source object's content has changed since it was last embedded. This is the storage layer for idempotent re-chunking.

## Acceptance Criteria

- [x] `EmbeddingRevision` model exists in `rag_chat/models.py` with fields:
  - `content_type` — ForeignKey to `ContentType` (same `limit_choices_to` as `ContentChunk`)
  - `object_id` — PositiveBigIntegerField
  - `source_hash` — CharField(max_length=64, null=True, blank=True)
  - `last_processed_at` — DateTimeField(auto_now=True)
- [x] Unique constraint on `(content_type, object_id)`.
- [x] Migration generated via `manage.py makemigrations`.
- [x] Data migration creates one `EmbeddingRevision` row per distinct `(content_type, object_id)` in `ContentChunk`, with `source_hash=None`.
- [x] `cleanup_orphaned_chunks` task in `rag_chat/tasks.py` extended to also delete `EmbeddingRevision` rows whose source object no longer exists.
- [x] Model registered in `rag_chat/admin.py` (read-only list display is sufficient).

## Notes

- `source_hash=None` on backfilled rows means "force reprocessing on next run" — this is intentional.
- The generic FK pattern mirrors `ContentChunk` but this model has one row per source object, not per chunk.
