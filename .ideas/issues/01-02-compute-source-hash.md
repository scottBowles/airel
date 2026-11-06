# Issue 01-02: Add `compute_source_hash` to content processors

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** 01-01
**Blocks:** 01-03

## Summary

Add a `compute_source_hash(obj)` method to `BaseContentProcessor` and implement `_hash_input(obj)` on each of the 7 processor subclasses. The hash reflects exactly the fields that the processor reads, normalized via `clean_text()`, so "what I embed" and "what I hash" always evolve together.

## Acceptance Criteria

- [x] `BaseContentProcessor` gains:
  - `compute_source_hash(self, obj) -> str` — calls `_hash_input(obj)`, runs `clean_text()`, returns `hashlib.sha256(...).hexdigest()`.
  - `_hash_input(self, obj) -> str` — abstract method returning concatenated field values.
- [x] Each subclass implements `_hash_input` with these fields:
  - `GameLogProcessor`: `log_text` + `title`
  - `CharacterProcessor`: `name` + `description` + `race.name` + sorted association names
  - `PlaceProcessor`: `name` + `description` + `place_type` + `parent.name`
  - `ItemProcessor`: `name` + `description`
  - `ArtifactProcessor`: `name` + `description` + sorted item names
  - `RaceProcessor`: `name` + `description`
  - `AssociationProcessor`: `name` + `description`
- [x] FK/M2M values use string names (not PKs). M2M names are sorted for stability. Missing FK values produce empty string (not `"None"`).
- [x] Unit tests for each processor subclass:
  - Hash is deterministic (same input → same hash).
  - Hash changes when a tracked field changes.
  - Hash does NOT change for whitespace-only differences.
  - Hash includes M2M/FK names where applicable (character, place, artifact).

## Notes

- `clean_text()` from `rag_chat/embeddings.py` is already used in the embedding pipeline. Reusing it here ensures the hash and the embedded text are normalized identically.
- When project 03 adds `compiled_summary` to `GameLog`, the only change is adding it to `GameLogProcessor._hash_input()`.
