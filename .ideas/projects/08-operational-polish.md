# Project 08 — Operational Polish

Project 08 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md).

Runs alongside or after project 04+. Pieces are independently grabbable and parallelizable.

## Goal

Make the system reliable, observable, and economical at steady-state. Pick up the loose ends from earlier projects: scheduling, retries, eval CI, dashboards, lifecycle cleanup, and an optional embedding-model evaluation.

## Decisions to nail down

1. **Re-embed scheduling per content type.**
   - Trigger rules: regenerate `narrative_summary` only when `last_appearance > narrative_summary_updated_at_session`; regenerate relations only when a new session involves them; analogous rules per type.
   - Coalescing windows for batch ingests.
   - Manual force-refresh paths.

2. **Cost and latency dashboards.**
   - Per-task-type metrics: compilation, embedding, narrative, relation, chat.
   - Storage: Django admin views, separate dashboard, or external log aggregator.
   - Alert thresholds.

3. **Retry and backoff tuning** for the longer-running compilation tasks (compared to today's `process_content`).
   - Retry counts and backoff curves per task type.
   - Dead-letter handling.
   - Idempotency requirements (interaction with `source_revision` from project 01).

4. **Eval-set CI.**
   - Where the eval set runs: CI on PRs touching `rag_chat/`, nightly, or both.
   - Pass/fail criteria and regression thresholds.
   - Result surfacing: PR comment, dashboard, email.

5. **Embedding-model swap (optional).**
   - Whether to evaluate open-source or cheaper embedding models.
   - Migration path if we swap, including vector-dim implications.
   - Decision criteria: cost per 1M tokens, recall on the eval set.

6. **Cleanup and lifecycle.**
   - When `ContentChunk` rows for legacy chunking strategies are pruned (continuation of project 04 cutover).
   - Archival policy for deleted entities, sessions, and suggestions.

## Out of scope

Anything that is a feature change rather than operational. New capabilities belong in their own project.

## Edge cases worth pressure-testing

- Items in this list that don't yet have a measurable problem they solve — defer those.
- Observability gaps that earlier projects assumed would be solved here.
- Conflicts between auto-trigger (project 01) and the scheduling rules proposed here.
- Cost regressions when the eval set runs on every PR.

## Definition of done for the grilling

Ready to create a PRD that distinguishes items shipping now from items deferred, with concrete acceptance criteria, metrics, and thresholds for each item that ships, plus a list of independently-grabbable issues.
