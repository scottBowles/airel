# Issue 01-03: Make `process_content` idempotent via hash check

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** 01-01, 01-02
**Blocks:** 01-04

## Summary

Integrate the `EmbeddingRevision` model and `compute_source_hash` into the existing `process_content` Celery task so that reprocessing unchanged content is a no-op.

## Acceptance Criteria

- [x] At the start of `process_content`, compute the current source hash via the processor's `compute_source_hash(obj)`.
- [x] Look up `EmbeddingRevision` for the `(content_type, object_id)` pair.
- [x] If `EmbeddingRevision.source_hash` matches and `force_reprocess=False`: return early with `{"status": "skipped", "reason": "hash_unchanged"}`. Do not delete or recreate chunks.
- [x] Remove (or keep as fallback) the existing `existing_chunks.exists()` skip check — the hash check supersedes it.
- [x] After successful chunk creation: upsert `EmbeddingRevision` with the new hash (using `update_or_create`).
- [x] `force_reprocess=True` bypasses the hash check entirely (existing behavior preserved).
- [x] Integration tests (mock `get_embedding` to return a fixed vector):
  - First call: creates chunks + `EmbeddingRevision`. Returns `"status": "processed"`.
  - Second call (same content): returns `"status": "skipped", "reason": "hash_unchanged"`. No new chunks.
  - Change a tracked field, call again: deletes old chunks, creates new ones, updates hash.
  - `force_reprocess=True`: always processes regardless of hash.

## Notes

- The existing `existing_chunks.exists()` check (without hash comparison) can be removed — it's a weaker version of the same idea. The hash check covers its intent and adds content-awareness.
- The task should still handle the "object not found" case gracefully (existing behavior).
