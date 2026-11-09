# Issue 01-05: Update management commands for signal-aware bulk operations

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** 01-04
**Blocks:** None

## Summary

Update the `create_logs` management command (and any other bulk-creation paths) to suppress embedding signals during the loop and dispatch a single batch re-embed at the end.

## Acceptance Criteria

- [x] `nucleus/management/commands/create_logs.py` wraps its bulk creation loop in the `disconnect_embedding_signals()` context manager from `rag_chat/signals.py`.
- [x] After the loop completes, enqueues `process_all_content.delay(content_types=["gamelog"], force_reprocess=False)`.
- [x] Comment block at the signal disconnect site explains:
  - Why signals are disconnected (bulk import would flood the queue).
  - That `process_all_content` is called automatically at the end.
  - If the command is interrupted, the user should run `python manage.py process_game_logs --types gamelog` manually to catch up. (The spec originally named `process_content --content-types gamelog`; that command and flag don't exist — the command module is `process_game_logs.py`.)
- [x] No other management commands currently do bulk entity creation, but if any are identified during implementation, apply the same pattern.

## Notes

- The `process_content` management command (`rag_chat/management/commands/process_game_logs.py`; despite its header comment, it is only invocable as `process_game_logs`) already exists and can serve as the documented "manual catch-up" path.
- This is a small issue — primarily wiring + documentation.
