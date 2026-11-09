"""
Recall@5: for each ``eval_type: retrieval`` case, every expected source must be
among the sources of the top 5 chunks RAGService.semantic_search returns for
the case's stored query embedding.
"""

import unittest

from django.test import TestCase

from .loaders import (
    GENERATED,
    RECALL_K,
    STANDIN,
    add_case_tests,
    missing_expected_sources,
    retrieve,
    retrieved_sources,
)


def check_recall(test: TestCase, case) -> None:
    results = retrieve(case)
    test.assertLessEqual(len(results), RECALL_K)
    missing = missing_expected_sources(case, results)
    test.assertEqual(
        missing,
        [],
        f"{case.id}: expected {case.expected_source_content_type} ids {missing} "
        f"not in the top {RECALL_K}; got {retrieved_sources(results)}",
    )
    if case.max_top_similarity is not None:
        scores = [round(result.similarity, 4) for result in results]
        test.assertTrue(
            all(score <= case.max_top_similarity for score in scores),
            f"{case.id}: similarities {scores} exceed {case.max_top_similarity}",
        )


class StandinRetrievalTests(TestCase):
    """The hand-made stand-in fixtures: proves the harness, runs everywhere."""

    @classmethod
    def setUpTestData(cls):
        STANDIN.load_into_db()


add_case_tests(StandinRetrievalTests, STANDIN, "retrieval", check_recall)


@unittest.skipUnless(
    GENERATED.is_ready(),
    "no generated fixtures yet: run rag_chat/eval/generate_fixtures.py with a real OpenAI key",
)
class RetrievalTests(TestCase):
    """Real chunks of the example logs and real query embeddings."""

    @classmethod
    def setUpTestData(cls):
        GENERATED.load_into_db()


add_case_tests(RetrievalTests, GENERATED, "retrieval", check_recall)
