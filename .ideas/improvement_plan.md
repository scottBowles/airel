# RAG Chat Improvement Plan

## Context for downstream agents

This plan is for the `dnd-api` Django repo (a tabletop-RPG campaign tool). The RAG chat system lets users ask natural-language questions about a long-running campaign and answers from persisted entities (Character, Place, Item, Race, Association, Artifact) and game session logs (`GameLog`).

### Current pipeline (as of writing)

**Persisted RAG models — `rag_chat/models.py`:**

- `ContentChunk`: chunk text + 1536-dim `VectorField` embedding, generic FK to source object, JSON `metadata`, `chunk_index`. HNSW pgvector index (cosine, m=16, ef_construction=64).
- `ChatSession`: has `conversation_summary` (running summary of older messages outside the sliding token window).
- `ChatMessage`: stores `sources` JSON, `tokens_used`, `similarity_threshold`, `included_in_summary`.

**Source content fields:**

- `GameLog` (`nucleus/models.py`) persists `title`, `brief`, `synopsis`, `summary`, `full_text`, `generated_log_text`, `full_text_search_vector` (GIN). On create, `update_from_google()` pulls title/full_text/date from Google Drive.
- Entity models (`Character`, `Place`, `Item`, `Race`, `Association`, `Artifact`) store `name`, `description`, `aliases`, m2m to `GameLog`. **No post_save signals** trigger embedding regeneration.
- Audio is transcribed by the separate `transcription/` app (own Celery queue) and lands in `GameLog.full_text`.

**Embedding pipeline — `rag_chat/embeddings.py`:**

- `get_embedding(text)` → OpenAI `text-embedding-3-small` (1536-dim).
- `chunk_document(text, chunk_size=800, overlap=100)` — sentence-boundary-aware splitter.
- `clean_text(text)` — whitespace/artifact normalization.

**Per-source-type processors — `rag_chat/content_processors.py`:** `BaseContentProcessor` subclasses for `gamelog`, `character`, `place`, `item`, `artifact`, `race`, `association`. Each produces `(chunk_text, metadata)` lists. Chunk thresholds 800–1200 words. `GameLogProcessor` reads `log_text` (full_text or Google doc) and includes `brief_summary`, `session_number`, `session_date`, `places_set_in` in metadata.

**Triggering — `rag_chat/tasks.py`:**

- `process_content(content_type, object_id, force_reprocess)` — Celery task, max_retries=3, exponential backoff.
- `process_all_content(content_types=None, force_reprocess, limit)` — batch dispatcher.
- `cleanup_orphaned_chunks()` — removes chunks for deleted sources.
- **Triggered only manually** via: admin action on `ContentChunkAdmin`, GraphQL mutations `RAGMutation.process_content` / `process_all_content` (superuser-only) in `rag_chat/types.py`, or management command `rag_chat/management/commands/process_game_logs.py` (note: command is named `process_content`).

**LLM-based pre-processing — `nucleus/ai_helpers.py`:**

- `openai_summarize_text` — `text-davinci-002`, JSON output (legacy).
- `openai_summarize_text_chat` — `gpt-3.5-turbo`, JSON `{title, brief, places, characters, races, associations, items}` — **current path**.
- `openai_titles_from_text_chat` — `gpt-3.5-turbo`, 5 alternative titles.
- `openai_shorten_text` — `code-davinci-002`, ~70% compression.
- These feed `nucleus/management/commands/create_ai_suggestions.py` and `create_ai_titles.py`, which populate `AILogSuggestion` records (curated `GameLog.title/brief/summary` fields when accepted). They do _not_ themselves write to `ContentChunk`.

**Live chat — `rag_chat/services/RAGService.py`:** orchestrates query enhancement (trigram + semantic + LLM rewrite via `gpt-3.5-turbo`), hybrid retrieval (FTS 0.3 / semantic 0.6 / trigram 0.1, z-score normalized in `services/normalize_and_hybrid_rank_fuse.py`), context assembly, and final response generation. Supporting services: `services/entity_extractor.py` (n-gram candidate extraction), `services/build_conversation_memory.py` (sliding-window summarizer updating `ChatSession.conversation_summary`), `services/trigram_entity_search.py`, `services/game_log_full_text_search.py`.

### Live chat pipeline (current `chat_stream_view`)

- **Entry:** `User + Permission` → `ChatSession`
- **Memory step:** `(Session, Query)` → `History String`. Splits messages by sliding token window; LLM merges old summary + newly-aging messages into updated summary; formats `(Summary + Included Messages)` → `conv_history_str`.
- **Enhancement step:** `(Query, conv_history_str)` → candidate entities (trigram + semantic) → LLM rewrite → `enhanced_query`.
- **Retrieval step:** entities and logs each get search → z-score normalize → rank fuse → filter (< mean − 1σ).
- **Assembly step:** builds context with conversation history, retrieved entities, summaries of _all_ logs, full text of retrieved logs up to token limit, query, system prompt. Injects `user_name` into system prompt; generates `SourcesModel`.
- **Output:** `generate_response_stream(Query, PreparedContext)`.

### Source-text characteristics (drove several plan decisions)

Three randomly-sampled raw logs in `.ideas/example_logs/` reveal:

1. Dialogue without speaker tags; pronouns drift constantly.
2. Aliases and renames mid-session (e.g., Carlos → Ego in 2019-04-04).
3. Typos and inconsistent spellings (`Horthulf` / `Hrothulf`); familiar/pet name conflation (`Hayete` / `Hiare`).
4. Heavy pop-culture metaphor ("Mark McGuire baseball swing", "Helm's Deep") — style, not facts.
5. Inside jokes and running gags that are nonetheless real plot beats.
6. OOC commentary mixed in ("DM is adamant…", player names like Greg/Joel).
7. Attempted vs. successful actions interleaved; outcomes inferred.
8. Critical lore in throwaway lines ("the egg is one of the nine power cells of the Solar Cannon"; "My sister awaits in the vault of Daedalus").
9. Real scene structure (room-by-room exploration) but no markup.
10. Variable length; some logs fall under the current 1000-word chunk threshold and become a single chunk.
11. Speculation vs. canon is unmarked; characters guess wrong constantly.

These characteristics make raw chunks a poor embedding surface and motivate canonicalization, structured extraction, and compiled summaries as primary retrieval surfaces.

### Key decisions already made

- Embedded surface should shift from raw chunked transcript → compiled artifacts (compiled_summary, key_decisions, unresolved_threads, lore_facts, scenes from canonicalized text).
- Curated/display fields (`summary`, `brief`, `synopsis`) stay user-editable; new `compiled_summary` is the LLM-owned RAG surface.
- New entities/relations from compilation are _suggestions for human review_, never auto-created.
- Agentic tool-use is deferred until compiled artifacts exist (Phase 1 prerequisite).

---

## Guiding principles

1. **Compiled artifacts beat raw text.** The raw logs are too noisy (pronouns, aliases, typos, metaphors, OOC commentary) to embed productively. Replace raw-chunk embedding with embedded _compiled_ artifacts; keep raw text retrievable for fidelity.
2. **Canonicalize early.** Fix typos and resolve aliases before compilation, so every downstream stage benefits.
3. **Structure first, prose second.** Extract structured fields (lore facts, key decisions, unresolved threads, entity appearances, alias updates) alongside prose summaries — they unlock thread-tracking queries and feed entity/relation compilation.
4. **Build foundations before changing control flow.** Compiled artifacts must exist before agentic tool-use is worth adding.
5. **Keep curated/display fields separate from RAG fields.** `summary`/`brief` stay user-editable; new `compiled_summary` is the LLM-owned retrieval surface.

---

## Phase 0 — Audit, instrumentation, hygiene

Goal: prepare the ground; fix easy wins; make later phases observable.

- **Audit `_assemble_context`** in `rag_chat/services/RAGService.py`: confirm exactly which log fields are concatenated as "summaries of all logs" today. Decide which field will be replaced by `compiled_summary` in Phase 1.
- **Auto-trigger embeddings**: add post_save signals (or explicit lifecycle hooks) on entity and `GameLog` models that queue `process_content`. The current "manual only" model will not scale once compilation tasks multiply.
- **Idempotent re-chunking**: add `ContentChunk.source_revision` (or content hash) so reprocessing unchanged content is a no-op.
- **OOC tagging heuristic**: detect and tag closing meta paragraphs, parenthetical DM asides, player-name references ("Greg / Joel / DM is adamant…") so they can be excluded from compilation but retained in raw text.
- **Typo normalization pre-pass**: cheap deterministic fuzzy-match on the entity roster (e.g., `Horthulf` → `Hrothulf`). No LLM needed in most cases.
- **Eval set**: a fixed list of (query, expected sources, expected answer keywords) test cases. Run after each phase to compare retrieval+answer quality.

Result: cleaner inputs, automatic refresh, measurable progress.

---

## Phase 1 — Session compilation (foundation)

Goal: produce per-session compiled artifacts that become the primary retrieval surface.

### New `GameLog` fields

- `compiled_summary` — TextField, 400–600 words, canonical names, the dominant embedded surface for "what happened" queries.
- `key_decisions` — JSONField (list of strings).
- `unresolved_threads` — JSONField (list of `{text, origin_session_id}`).
- `lore_facts` — JSONField (list of `{text, subject_entity_id?}`).
- `canonical_full_text` — TextField, optional, raw text rewritten with canonical names.
- Keep `full_text`, `summary`, `brief`, `synopsis` as-is.

### New through-model

- `SessionEntityAppearance(session, entity, canonical_quotes[], significance)` — replaces/augments existing m2m relations.

### New compilation task

`compile_session(game_log_id)` in `rag_chat/tasks.py`:

1. Inputs: `full_text`, prior session's `compiled_summary` for continuity, full canonical entity roster + alias map.
2. Pre-pass: typo normalization → canonicalization (alias substitution) → `canonical_full_text`.
3. LLM call with structured output schema returning:
   - `compiled_summary` (prose, canonical names)
   - `scenes[]` (`{title, canonical_text, char_range}`)
   - `key_decisions[]`, `unresolved_threads[]`, `lore_facts[]`
   - `entity_appearances[]` (entity_id, significance, quotes)
   - `new_entity_candidates[]` (name, type guess, evidence)
   - `alias_updates[]` (entity_id, new_alias)
   - `relationship_changes[]` (entity_a, entity_b, change description)
4. Two-pass prompt structure: literal outline ("what canonically happened") → prose render. Suppresses metaphor/joke leakage.
5. Persist all fields; create `SessionEntityAppearance` rows; apply `alias_updates`; queue `new_entity_candidates` and `relationship_changes` for human review (new `EntitySuggestion` / `RelationSuggestion` models, mirroring `AILogSuggestion`).

### Embedding changes

Update `GameLogProcessor` in `rag_chat/content_processors.py` to embed:

- `compiled_summary` as one chunk (`metadata.kind = "compiled_summary"`).
- Each `key_decision`, `unresolved_thread`, `lore_fact` as its own short chunk (`metadata.kind`, plus subject/origin metadata).
- Each scene from `canonical_full_text` as a chunk (`metadata.kind = "scene"`, with scene title).
- Drop fixed-word chunking of raw `full_text` as the primary retrieval surface.

### Assembly changes

In `_assemble_context`:

- Inject `compiled_summary` for every retrieved log (replaces the current "summaries of all logs" surface).
- For top-ranked logs, also inject `key_decisions`, `unresolved_threads`, `lore_facts`.
- Keep raw `full_text` available up to token budget for highly-ranked logs.

Result: dramatically better retrieval (canonical names, less noise), structured thread tracking, scene-level citation anchors.

---

## Phase 2 — Entity narrative summaries

Goal: capture what each entity has _become_, not just what it _is_.

### New entity fields

On each entity model (`Character`, `Place`, `Item`, `Race`, `Association`, `Artifact`):

- `narrative_summary` — TextField.
- `narrative_summary_updated_at_session` — FK or int, for incremental refresh.

### New compilation task

`compile_entity_narrative(entity_type, entity_id)`:

1. Inputs: existing `description`, prior `narrative_summary`, `SessionEntityAppearance` rows since `narrative_summary_updated_at_session`.
2. LLM call returning updated narrative summary (3–8 sentences depending on entity prominence).
3. Triggered at the end of `compile_session` for each entity that appeared in that session — incremental and cheap.

### Embedding changes

Each entity processor embeds `narrative_summary` as a high-priority chunk (`metadata.kind = "narrative_summary"`), so retrieval can prefer it for "what is X up to now?" queries. Existing description/aliases chunks remain as fallback fidelity.

Result: queries about character arcs, place state, and item history get directly relevant text instead of stitched-together log excerpts.

---

## Phase 3 — Entity relation summaries

Goal: capture themes/states/relationships that don't live in either-side entity records.

### New model

`EntityRelation`:

- Generic FKs to two entities, with a unique constraint on the unordered pair.
- `compiled_summary` — TextField, 3–5 sentences.
- `last_updated_session` — FK.
- `relation_type` — free-text, optional. Defer enum until corpus shape is clear.
- `confidence` — optional.

### New compilation task

`compile_relation(entity_a_id, entity_b_id, session_id)`:

1. Inputs: existing `EntityRelation` (if any) + relevant excerpts from the new session (drawn from canonicalized scene text and quotes).
2. LLM call returning updated 3–5 sentence relational summary.
3. Triggered from `compile_session`: for each pair of entities co-occurring in the session, queue this task.

### Embedding & retrieval

- Register `EntityRelationProcessor` and add `entity_relation` to `CONTENT_PROCESSORS` and `rag_chat/source_models.py`. Embed `compiled_summary`.
- In retrieval, when ≥2 entities surface for a query, look up their `EntityRelation` rows and inject the summaries into context as a structured boost.

Result: "What's between X and Y?" type queries answered directly; covers the theme/state/relationship gap that plain entity records can't.

---

## Phase 4 — Agentic tool-use (gated on Phase 1 quality)

Goal: lean default context, fidelity on demand.

### Refactor `RAGService.generate_response`

Add a tool-calling variant. Initial context becomes:

- Conversation history.
- `compiled_summary` for _all_ logs (with stable IDs) — a rolling table-of-contents.
- Top-k retrieved entity `narrative_summary`.
- Relevant `EntityRelation.compiled_summary`.

### Tools the agent can call

- `fetch_full_log(ids: list[str])` — raw `full_text` for those logs.
- `fetch_scene(session_id, scene_index)` — single canonicalized scene.
- `fetch_entity(id)` — full entity record + narrative_summary.
- `fetch_relation(entity_a, entity_b)` — relation summary.
- `fetch_unresolved_threads(filter?)` — open mysteries / clues.
- `fetch_lore_facts(subject_id?)` — canonical lore claims.

### Operational guardrails

- Cap tool-call rounds (e.g., 2).
- Cap total tokens.
- Stream final answer the same way `generate_response_stream` does today.
- Add a cheap query-classification heuristic to skip tool calls entirely for simple chitchat.

Result: model sees the big picture by default, pulls fidelity only when needed; solves token-budget squeeze and "which log do I trust" simultaneously.

---

## Phase 5 — Operational polish (parallelizable)

- Per-content-type re-embed scheduling (regenerate `narrative_summary` only when `last_appearance > narrative_summary_updated_at_session`).
- Cost/latency dashboards per task type.
- Retry/backoff tuning for compilation tasks (longer than current `process_content`).
- Eval-set CI: regression-detect retrieval quality drops between deploys.
- Optional: open-source embedding model swap if cost matters at scale.

---

## What we explicitly chose NOT to do (and why)

- **Replace chunking with full logs entirely** — counterproductive; chunking is how retrieval localizes. We change _what_ gets chunked (compiled artifacts + scenes), not whether we chunk.
- **Concrete relation-type enum upfront** — premature schema lock-in. Free-text labels first; categorize later if patterns emerge.
- **AI-filled entity descriptions as a top priority** — overlaps with `narrative_summary` and risks overwriting curated content. If we do it, it's a `Suggestion`-style flow mirroring `AILogSuggestion`, not a direct write.
- **Auto-create new entities from `new_entity_candidates`** — too risky given speculation/joke noise in source text. Always queue for human review.

---

## Dependency graph

```
Phase 0 (hygiene)
   │
   ▼
Phase 1 (session compilation) ─────────┐
   │                                   │
   ├──► Phase 2 (entity narratives)    │
   │       │                           │
   │       └──► Phase 3 (relations) ◄──┘
   │              │
   ▼              ▼
        Phase 4 (agentic tool-use)
   │
   ▼
Phase 5 (polish, runs alongside any later phase)
```

Phase 1 is the keystone. Everything past it is a relatively independent improvement on top of the same compiled-artifact substrate.
