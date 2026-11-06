# Issue 01-05: Update management commands for signal-aware bulk operations

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** 01-04
**Blocks:** None

## Summary

Update the `create_logs` management command (and any other bulk-creation paths) to suppress embedding signals during the loop and dispatch a single batch re-embed at the end.

## Acceptance Criteria

- [ ] `nucleus/management/commands/create_logs.py` wraps its bulk creation loop in the `disconnect_embedding_signals()` context manager from `rag_chat/signals.py`.
- [ ] After the loop completes, enqueues `process_all_content.delay(content_types=["gamelog"], force_reprocess=False)`.
- [ ] Comment block at the signal disconnect site explains:
  - Why signals are disconnected (bulk import would flood the queue).
  - That `process_all_content` is called automatically at the end.
  - If the command is interrupted, the user should run `python manage.py process_content --content-types gamelog` manually to catch up.
- [ ] No other management commands currently do bulk entity creation, but if any are identified during implementation, apply the same pattern.

## Notes

- The `process_content` management command (in `rag_chat/management/commands/process_game_logs.py`, aliased as `process_content`) already exists and can serve as the documented "manual catch-up" path.
- This is a small issue — primarily wiring + documentation.
