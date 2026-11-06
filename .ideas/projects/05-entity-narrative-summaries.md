# Project 05 — Entity Narrative Summaries

Project 05 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md).

Depends on project 03 (session compilation populates `SessionEntityAppearance` rows that feed this project).

## Goal

Capture what each entity has _become_ across the campaign, separate from its static `description`. Compile a per-entity `narrative_summary` from the structured appearance data emitted by project 03, embed it as a high-priority retrieval surface, and keep it independent from user-curated display fields.

## Decisions to nail down

1. **New entity fields** on each of `Character`, `Place`, `Item`, `Race`, `Association`, `Artifact`.
   - `narrative_summary` — TextField. Lock length target, tone, and constraints (canonical names; distinguish "what X is" from "what X has become").
   - `narrative_summary_updated_at_session` — FK or int.
   - Shared abstract base vs. per-model migration.

2. **`compile_entity_narrative` task contract.**
   - Inputs: existing `description`, prior `narrative_summary`, `SessionEntityAppearance` rows since `narrative_summary_updated_at_session`, and possibly related entities or curated `summary` fields.
   - Incremental update vs. full rewrite vs. mode chosen by appearance count.
   - Length scaling by entity prominence (one-line cameo vs. campaign mainstay).
   - LLM model choice and cost ceiling per run.
   - Failure modes: entity removed mid-run, contradictory appearances, no appearances at all.

3. **Triggering.**
   - Fan-out from `compile_session` for every appearing entity vs. separate scheduled pass.
   - Coalescing across batch ingests so a single entity is not compiled five times for five back-to-back sessions.
   - Manual trigger paths (admin action, GraphQL mutation).

4. **Embedding and retrieval.**
   - Each entity processor in `content_processors.py` embeds `narrative_summary` as a high-priority chunk (`metadata.kind = "narrative_summary"`).
   - Interaction with existing description / aliases chunks: replace, augment, or reweight.
   - How retrieval prefers narrative summaries for "what is X up to now?" queries.

5. **Display vs. RAG separation.** Confirm `narrative_summary` is LLM-owned and not shown in user-facing entity pages without explicit opt-in. Define admin/review surfaces.

## Out of scope

Relation summaries (project 06). Agentic tool-use (project 07).

## Edge cases worth pressure-testing

- Entities with very few appearances.
- Entities that change ownership (an item passed between characters).
- Entities destroyed in-fiction (does the summary reflect their end state?).
- Non-character entities — what does "current state" mean for a Place, an Item, a Race?
- Entities renamed mid-campaign (Carlos / Ego from the example logs).
- Entities with contradictory appearances across sessions.
- Sample-log entities to test prompt design: Hrothulf, Ego/Carlos, the egg, the Solar Cannon, House Roderick.

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria covering schema, task contract, triggering, retrieval integration, and the display/RAG boundary, plus a list of independently-grabbable issues.
