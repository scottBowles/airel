# Project 06 — Entity Relation Summaries

Project 06 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md).

Depends on project 03 (session compilation emits `relationship_changes[]` and `entity_appearances[]` for pair detection). Benefits from project 05 (entity narratives provide single-side context).

## Goal

Capture themes, states, and dynamics that live between two entities rather than within either alone — the gap that plain entity records can't fill. Compile per-pair `EntityRelation` summaries from session-compilation output, embed them, and inject them at chat time when ≥2 entities surface for a query.

## Decisions to nail down

1. **`EntityRelation` model.**
   - Generic FK to two entities with a unique constraint on the unordered pair, and how "unordered" is enforced (sorted IDs in a third column, hash, signal-enforced ordering).
   - Cross-type pairs (Character ↔ Place, Character ↔ Item, etc.) — which combinations are allowed.
   - `compiled_summary` — TextField, 3–5 sentences, canonical names.
   - `relation_type` — free-text default; confirm enum is deferred.
   - `last_updated_session` — FK.
   - `confidence` — definition and who sets it.
   - Lifecycle: how a relation becomes stale or gets archived when entities no longer interact.

2. **`compile_relation` task contract.**
   - Inputs: existing `EntityRelation` (if any), `SessionEntityAppearance` excerpts for the new session, optionally each side's `narrative_summary`.
   - Pair-detection rule from `compile_session`: every co-occurring pair, every pair flagged in `relationship_changes[]`, or thresholded by significance.
   - LLM model choice and cost ceiling — pair counts can grow quadratically with cast size.
   - Failure modes: entity merged or deleted, contradictions, single-side context.

3. **Triggering and coalescing.**
   - Fan-out from `compile_session` vs. separate scheduled pass.
   - Coalescing across batch ingests so a single pair is not compiled multiple times.
   - Cost guardrails: cap pairs per session, prioritize by significance.

4. **Embedding and retrieval.**
   - Register `EntityRelationProcessor`; add `entity_relation` to `CONTENT_PROCESSORS` and `rag_chat/source_models.py`. Embed `compiled_summary`.
   - In `_assemble_context`, when ≥2 entities surface for a query, look up matching `EntityRelation` rows and inject summaries. Lock format and budget.
   - Whether relation chunks participate in the standard hybrid retrieval, only in a structured boost lookup, or both.

5. **Symmetry, directionality, asymmetry.**
   - Single symmetric summary per pair vs. two directional summaries.
   - How "X owes Y" or "Y employs X" asymmetries are expressed within a single `compiled_summary`.

## Out of scope

Agentic tool-use (project 07). Operational polish (project 08).

## Edge cases worth pressure-testing

- Mass-NPC scenes generating dozens of pairs of marginal significance.
- Party-internal vs. party-external relations.
- Entities that meet only once, briefly.
- Asymmetric relations where one side dominates the dynamic.
- Entities merged or deleted after a relation row exists.
- Relations the party only learns about second-hand (and may be wrong about).
- Cost validation against the example logs: how many real pairs per session, how many LLM calls per session.

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria, including pair-detection thresholds and cost bounds, plus a list of independently-grabbable issues.
