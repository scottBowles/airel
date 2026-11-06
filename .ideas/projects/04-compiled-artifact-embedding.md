# Project 04 — Compiled-Artifact Embedding & Assembly Migration

Project 04 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md).

Depends on project 03 (session compilation must be writing the new fields).

## Goal

Wire the artifacts produced by project 03 into the retrieval and assembly path. Replace today's fixed-word chunking of raw `full_text` with embeddings of compiled summaries, structured fields, and canonicalized scenes. Migrate `_assemble_context` to consume the new shape without regressing retrieval quality on the eval set.

## Decisions to nail down

1. **`GameLogProcessor` rework** in `rag_chat/content_processors.py`.
   - Which compiled artifacts get embedded as their own chunks: `compiled_summary`, each `key_decision`, each `unresolved_thread`, each `lore_fact`, each scene from `canonical_full_text`.
   - `metadata.kind` taxonomy and how retrieval uses it (boost weights, filtering).
   - Whether the legacy fixed-word chunking of raw `full_text` is removed entirely, kept as fallback, or kept for a transition window.
   - Chunk-size decisions for short artifacts (single-sentence lore facts vs. 800-word scenes).

2. **`_assemble_context` rework** in `rag_chat/services/RAGService.py`.
   - How `compiled_summary` is injected for retrieved logs and whether it is included for _all_ logs as a rolling table-of-contents (anticipating project 07's agentic mode).
   - How `key_decisions`, `unresolved_threads`, `lore_facts` are formatted in the prompt.
   - When (or whether) raw `full_text` is included for highly-ranked logs.
   - Priority order across artifact kinds when the token budget is tight.

3. **Hybrid retrieval interaction.** Today retrieval fuses FTS, semantic, and trigram scores in `services/normalize_and_hybrid_rank_fuse.py`.
   - Whether `metadata.kind` should bias scoring (e.g., `compiled_summary` chunks weighted higher).
   - How retrieval avoids returning the same log via multiple chunk kinds (dedupe).
   - Whether thread-tracking queries ("what's the clew?") get a different retrieval recipe.

4. **Cutover plan.**
   - Run old and new chunking in parallel via feature flag, or hard cutover.
   - Backfill order (newest first, oldest first, all-at-once).
   - Disposition of existing `ContentChunk` rows from the old strategy.
   - Eval-set comparison criteria to confirm no regression before cutover completes.

## Out of scope

The compilation logic itself (project 03). Entity narrative embeddings (05). Relation embeddings (06). Agent tools (07).

## Edge cases worth pressure-testing

- Very short sessions whose `compiled_summary` is the entire signal.
- Sessions with zero `key_decisions` or zero `unresolved_threads`.
- Sessions with 30+ lore facts blowing up chunk counts.
- Token-budget pressure forcing artifact-kind dropping mid-prompt.
- Same log surfacing through multiple chunk kinds and dominating retrieval.
- Eval cases where the legacy chunking outperformed the compiled surface.

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria, including eval-set deltas required before cutover, plus a list of independently-grabbable issues covering the processor rework, the assembly rework, the retrieval changes, and the migration steps.
