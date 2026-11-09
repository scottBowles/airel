"""
Load eval cases and fixture data, and run retrieval for a case without OpenAI.

The spec (.ideas/issues/01-06-eval-infrastructure.md) puts this in a pytest
``conftest.py``. This repo runs tests with Django's test runner, which ignores
conftest files, so the loading lives here and the test modules call it from
``setUpTestData``.

Two fixture sets share this code:

- ``STANDIN`` (``standin/``): a handful of hand-written chunks with small fake
  vectors. It proves the harness and always runs, in CI too.
- ``GENERATED`` (``cases.yaml`` and ``fixtures/``): real chunks of the three
  example logs and real query embeddings, written by ``generate_fixtures.py``.
  Its tests skip until that script has been run.
"""

import importlib
import unittest
import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

import yaml
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from nucleus.models import GameLog
from rag_chat.models import ContentChunk

EVAL_DIR = Path(__file__).resolve().parent

#: Recall is measured over the top K retrieved chunks.
RECALL_K = 5

EMBEDDING_DIMENSIONS: int = ContentChunk._meta.get_field("embedding").dimensions

EVAL_TYPES = ("retrieval", "context_assembly")
DIFFICULTIES = ("easy", "medium", "hard")

REQUIRED_CASE_KEYS = (
    "id",
    "query",
    "query_embedding",
    "expected_source_content_type",
    "expected_source_ids",
    "eval_type",
    "difficulty",
    "notes",
)

# The module, not the class that rag_chat.services re-exports under the same name.
_rag_service_module = importlib.import_module("rag_chat.services.RAGService")


class FixtureError(ValueError):
    """An eval case or fixture file is malformed."""


@dataclass(frozen=True)
class EvalCase:
    id: str
    query: str
    query_embedding: list[float] | None
    expected_source_content_type: str
    expected_source_ids: list[int]
    eval_type: str
    difficulty: str
    notes: str
    # Optional keys beyond the spec's case shape:
    # substrings the assembled context must contain (context_assembly only)
    expected_content: list[str] = field(default_factory=list)
    # substrings the assembled context must not contain (context_assembly only)
    forbidden_content: list[str] = field(default_factory=list)
    # every retrieved chunk must score at or below this (for negative cases)
    max_top_similarity: float | None = None
    # the pipeline is known to fail this case today; the test is an expected failure
    known_gap: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "EvalCase":
        missing = [key for key in REQUIRED_CASE_KEYS if key not in data]
        if missing:
            raise FixtureError(f"case {data.get('id', '?')!r} is missing {missing}")
        unknown = set(data) - set(cls.__dataclass_fields__)
        if unknown:
            raise FixtureError(
                f"case {data['id']!r} has unknown keys {sorted(unknown)}"
            )
        case = cls(**data)
        if case.eval_type not in EVAL_TYPES:
            raise FixtureError(
                f"case {case.id!r}: eval_type must be one of {EVAL_TYPES}"
            )
        if case.difficulty not in DIFFICULTIES:
            raise FixtureError(
                f"case {case.id!r}: difficulty must be one of {DIFFICULTIES}"
            )
        if case.query_embedding is not None:
            pad_embedding(case.query_embedding)  # validates the length
        return case


@dataclass(frozen=True)
class FixtureSet:
    name: str
    cases_path: Path
    chunks_path: Path
    source_objects_path: Path

    def load_cases(self) -> list[EvalCase]:
        with self.cases_path.open() as f:
            data = yaml.safe_load(f) or {}
        cases = [EvalCase.from_dict(case) for case in data.get("cases", [])]
        ids = [case.id for case in cases]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise FixtureError(f"{self.cases_path}: duplicate case ids {duplicates}")
        return cases

    def cases(self, eval_type: str) -> list[EvalCase]:
        return [case for case in self.load_cases() if case.eval_type == eval_type]

    def is_ready(self) -> bool:
        """True once the fixture files exist and every case has an embedding."""
        if not (self.chunks_path.exists() and self.source_objects_path.exists()):
            return False
        return all(case.query_embedding is not None for case in self.load_cases())

    def load_into_db(self) -> None:
        """Create the source objects, then their chunks, in the test database."""
        with self.source_objects_path.open() as f:
            load_source_objects(json.load(f))
        with self.chunks_path.open() as f:
            load_chunks(json.load(f))


STANDIN = FixtureSet(
    name="standin",
    cases_path=EVAL_DIR / "standin" / "cases.yaml",
    chunks_path=EVAL_DIR / "standin" / "chunks.json",
    source_objects_path=EVAL_DIR / "standin" / "source_objects.json",
)

GENERATED = FixtureSet(
    name="generated",
    cases_path=EVAL_DIR / "cases.yaml",
    chunks_path=EVAL_DIR / "fixtures" / "chunks.json",
    source_objects_path=EVAL_DIR / "fixtures" / "source_objects.json",
)


def pad_embedding(vector: list[float]) -> list[float]:
    """
    Zero-pad a vector to the column's 1536 dimensions.

    Padding with zeros changes no dot product or norm, so cosine similarity is
    the same as for the short vector. That lets the stand-in fixtures use small
    hand-written vectors.
    """
    if len(vector) > EMBEDDING_DIMENSIONS:
        raise FixtureError(
            f"embedding has {len(vector)} dimensions; the column holds {EMBEDDING_DIMENSIONS}"
        )
    if not any(vector):
        raise FixtureError("embedding is all zeros, so cosine similarity is undefined")
    return list(vector) + [0.0] * (EMBEDDING_DIMENSIONS - len(vector))


def _model_for(label: str):
    app_label, model_name = label.split(".")
    return apps.get_model(app_label, model_name)


def load_source_objects(records: list[dict]) -> None:
    """
    Create source objects from ``{"model": "app.model", "pk": ..., "fields": {...}}``
    records (the shape of Django's serializer, many-to-many fields excluded).

    GameLogs go through ``bulk_create``, which skips ``GameLog.save()`` and so its
    fetch from Google Drive. Other models use ``objects.create`` so that their
    save() fills derived fields such as slugs.
    """
    for record in records:
        model = _model_for(record["model"])
        fields = {
            name: model._meta.get_field(name).to_python(value)
            for name, value in record["fields"].items()
        }
        instance = model(pk=record["pk"], **fields)
        if model is GameLog:
            GameLog.objects.bulk_create([instance])
        else:
            instance.save()


def load_chunks(records: list[dict]) -> None:
    """Create ContentChunks from records written by generate_fixtures.py."""
    chunks = []
    for record in records:
        app_label, model_name = record["content_type"].split(".")
        chunks.append(
            ContentChunk(
                content_type=ContentType.objects.get_by_natural_key(
                    app_label, model_name
                ),
                object_id=record["object_id"],
                chunk_index=record["chunk_index"],
                chunk_text=record["chunk_text"],
                metadata=record.get("metadata", {}),
                embedding=pad_embedding(record["embedding"]),
            )
        )
    ContentChunk.objects.bulk_create(chunks)


@contextmanager
def no_openai() -> Iterator[None]:
    """Fail loudly if anything reaches the OpenAI client."""

    def refuse(*args, **kwargs):
        raise AssertionError("the retrieval eval must not call OpenAI")

    with patch("nucleus.ai.get_client", side_effect=refuse):
        yield


def _approximate_token_count(text: str, model: str = "") -> int:
    # count_tokens' own offline fallback; real tiktoken would download its
    # encoding on first use, and the eval data is far below any token budget.
    return len(text) // 4


@contextmanager
def offline_pipeline(case: EvalCase) -> Iterator[None]:
    """
    Run RAGService code as production does, except that the query embedding
    comes from the case and nothing touches the network.
    """
    if case.query_embedding is None:
        raise FixtureError(
            f"case {case.id!r} has no query_embedding; run generate_fixtures.py"
        )
    embedding = pad_embedding(case.query_embedding)

    def stored_embedding(text: str) -> list[float]:
        if text != case.query:
            raise AssertionError(
                f"case {case.id!r}: unexpected embedding request for {text!r}"
            )
        return embedding

    with (
        no_openai(),
        patch.object(
            _rag_service_module, "get_embedding", side_effect=stored_embedding
        ),
        patch.object(
            _rag_service_module, "count_tokens", side_effect=_approximate_token_count
        ),
    ):
        yield


def retrieve(case: EvalCase, k: int = RECALL_K):
    """Top-k chunks from RAGService.semantic_search for the case's stored embedding."""
    service = _rag_service_module.RAGService()
    with offline_pipeline(case):
        return service.semantic_search(case.query, limit=k)


def retrieved_sources(results) -> list[tuple[str, int]]:
    """``(content_type, object_id)`` of each result's source, deduplicated, in rank order."""
    sources: list[tuple[str, int]] = []
    for result in results:
        key = (result.content_type, result.content_object.pk)
        if key not in sources:
            sources.append(key)
    return sources


def missing_expected_sources(case: EvalCase, results) -> list[int]:
    """Expected source ids absent from the results (empty means recall@k is 1.0)."""
    found = {
        object_id
        for content_type, object_id in retrieved_sources(results)
        if content_type == case.expected_source_content_type
    }
    return [
        object_id for object_id in case.expected_source_ids if object_id not in found
    ]


def assemble_context(case: EvalCase, results) -> str:
    """
    Split retrieved sources into logs and entities the way RAGService passes
    them on, and return what ``_assemble_context`` builds from them.
    """
    logs: list = []
    entities: list = []
    for result in results:
        bucket = logs if isinstance(result.content_object, GameLog) else entities
        if result.content_object not in bucket:
            bucket.append(result.content_object)
    service = _rag_service_module.RAGService()
    with offline_pipeline(case):
        assembled, _ = service._assemble_context("", entities, logs)
    return assembled


def add_case_tests(test_class, fixture_set: FixtureSet, eval_type: str, check) -> None:
    """
    Add one test method per case of ``eval_type`` to ``test_class``, standing in
    for pytest parametrization: ``check(test_case, eval_case)`` runs each one, and
    the method is named after the case id so a failure names the case.
    """
    for case in fixture_set.cases(eval_type):

        def test(self, case=case):
            check(self, case)

        test.__doc__ = f"{case.id} ({case.difficulty}): {case.query}"
        if case.known_gap:
            test = unittest.expectedFailure(test)
        name = "test_" + case.id.replace("-", "_")
        if hasattr(test_class, name):
            raise FixtureError(f"two cases map to the test name {name}")
        setattr(test_class, name, test)
