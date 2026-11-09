"""
Checks on the eval harness itself, so a broken loader or a check that cannot
fail does not pass for a working eval.
"""

from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from rag_chat.embeddings import get_embedding
from rag_chat.models import ContentChunk

from . import generate_fixtures
from .loaders import (
    EMBEDDING_DIMENSIONS,
    EVAL_TYPES,
    GENERATED,
    STANDIN,
    EvalCase,
    FixtureError,
    missing_expected_sources,
    no_openai,
    pad_embedding,
    retrieve,
)

SEED_CATEGORIES = 9  # the spec's seed case categories


class CaseFileTests(SimpleTestCase):
    def test_generated_cases_are_valid(self):
        cases = GENERATED.load_cases()
        self.assertGreaterEqual(len(cases), SEED_CATEGORIES)
        self.assertEqual({case.eval_type for case in cases}, set(EVAL_TYPES))

    def test_generated_cases_point_at_example_logs(self):
        log_ids = {pk for pk, _, _ in generate_fixtures.LOGS}
        for case in GENERATED.load_cases():
            self.assertEqual(case.expected_source_content_type, "gamelog", case.id)
            self.assertLessEqual(set(case.expected_source_ids), log_ids, case.id)

    def test_standin_covers_both_eval_types(self):
        self.assertEqual(
            {case.eval_type for case in STANDIN.load_cases()}, set(EVAL_TYPES)
        )

    def test_case_missing_a_key_is_rejected(self):
        with self.assertRaises(FixtureError):
            EvalCase.from_dict({"id": "x", "query": "q"})

    def test_case_with_unknown_eval_type_is_rejected(self):
        data = vars(STANDIN.load_cases()[0]) | {"eval_type": "answer_quality"}
        with self.assertRaises(FixtureError):
            EvalCase.from_dict(data)


class PadEmbeddingTests(SimpleTestCase):
    def test_pads_to_column_width(self):
        padded = pad_embedding([0.5, 1.0])
        self.assertEqual(len(padded), EMBEDDING_DIMENSIONS)
        self.assertEqual(padded[:2], [0.5, 1.0])
        self.assertFalse(any(padded[2:]))

    def test_rejects_too_long(self):
        with self.assertRaises(FixtureError):
            pad_embedding([1.0] * (EMBEDDING_DIMENSIONS + 1))

    def test_rejects_all_zeros(self):
        with self.assertRaises(FixtureError):
            pad_embedding([0.0, 0.0])


class FillQueryEmbeddingsTests(SimpleTestCase):
    def test_replaces_only_embedding_lines(self):
        text = "# keep me\ncases:\n  - id: a\n    query: q\n    query_embedding: null\n    notes: n\n"
        filled = generate_fixtures.fill_query_embeddings(text, {"a": [0.25, -1.0]})
        self.assertEqual(filled, text.replace("null", "[0.25, -1.0]"))

    def test_unplaced_case_fails(self):
        with self.assertRaises(SystemExit):
            generate_fixtures.fill_query_embeddings("cases:\n  - id: a\n", {"a": [1.0]})


class HarnessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        STANDIN.load_into_db()

    def test_standin_fixtures_load(self):
        self.assertEqual(ContentChunk.objects.count(), 9)

    def test_recall_check_reports_a_miss(self):
        solar = next(c for c in STANDIN.load_cases() if c.id == "standin-solar-cannon")
        wrong = EvalCase(**(vars(solar) | {"expected_source_ids": [101, 103]}))
        self.assertEqual(missing_expected_sources(wrong, retrieve(wrong)), [103])

    def test_recall_check_matches_content_type(self):
        solar = next(c for c in STANDIN.load_cases() if c.id == "standin-solar-cannon")
        as_character = EvalCase(
            **(vars(solar) | {"expected_source_content_type": "character"})
        )
        # gamelog 101 is retrieved; character 101 is not.
        self.assertEqual(
            missing_expected_sources(as_character, retrieve(as_character)), [101]
        )

    def test_retrieval_uses_stored_embedding(self):
        case = STANDIN.load_cases()[0]
        with patch("nucleus.ai.embed") as embed:
            retrieve(case)
        embed.assert_not_called()

    def test_openai_guard_refuses_calls(self):
        with no_openai(), self.assertRaisesMessage(
            AssertionError, "must not call OpenAI"
        ):
            get_embedding("anything")
