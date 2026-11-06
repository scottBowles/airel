# Issue 01-04: Add auto-trigger signals for embedding regeneration

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** 01-03
**Blocks:** 01-05

## Summary

Add Django signals that automatically enqueue `process_content` when GameLog or entity models are saved or their tracked M2M relationships change. Includes a rate limit on the task and a context manager for suppressing signals during bulk operations.

## Acceptance Criteria

- [ ] New file `rag_chat/signals.py` with:
  - `post_save` handler for: `GameLog`, `Character`, `Place`, `Item`, `Artifact`, `Race`, `Association`.
  - `m2m_changed` handler for: `Character.associations`, `GameLog.places_set_in`, `Artifact.items`.
  - `m2m_changed` handler fires on `post_add`, `post_remove`, `post_clear` actions only (not `pre_*`).
  - Both handlers call `process_content.delay(content_type_str, str(instance.pk))`.
- [ ] Signals registered in `RagChatConfig.ready()` in `rag_chat/apps.py`.
- [ ] Comment on signal handler documenting the invariant: "Signal handlers must not write back to the source model — the hash guard is naturally self-terminating because process_content writes only to ContentChunk."
- [ ] `process_content` task decorator gains `rate_limit="30/m"`.
- [ ] Reusable context manager `disconnect_embedding_signals()` exported from `rag_chat/signals.py` that disconnects all embedding signals on enter and reconnects on exit. For use in management commands.

## Notes

- `post_save` does NOT fire on M2M changes — that's why `m2m_changed` is needed separately.
- `Character.race` is a FK, so changes to it fire `post_save` on `Character` — no special handling needed.
- `Place.parent` is a FK, so changes to it fire `post_save` on `Place` — no special handling needed.
- The rate limit is a safety net, not a primary throttle. At ~150 logs and organic entity editing, the default queue handles the volume.
- No tests for signal wiring in this issue — signal correctness is verified manually and by integration tests in later projects.
