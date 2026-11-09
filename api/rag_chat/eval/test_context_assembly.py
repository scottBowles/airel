"""
Context assembly: for each ``eval_type: context_assembly`` case, retrieve the
top 5 chunks, pass their sources to RAGService._assemble_context, and check
that the expected sources' content reaches the assembled context.
"""

import unittest

from django.test import TestCase

from rag_chat.content_processors import get_processor

from .loaders import (
    GENERATED,
    STANDIN,
    add_case_tests,
    assemble_context,
    missing_expected_sources,
    retrieve,
    retrieved_sources,
)


def check_context(test: TestCase, case) -> None:
    results = retrieve(case)
    missing = missing_expected_sources(case, results)
    test.assertEqual(
        missing,
        [],
        f"{case.id}: expected ids {missing} were not retrieved; got {retrieved_sources(results)}",
    )
    assembled = assemble_context(case, results)

    by_id = {result.content_object.pk: result.content_object for result in results}
    for object_id in case.expected_source_ids:
        source = by_id[object_id]
        test.assertIn(
            get_processor(source).format_for_llm(source),
            assembled,
            f"{case.id}: {case.expected_source_content_type} {object_id} is not in the context",
        )
    for text in case.expected_content:
        test.assertIn(text, assembled, f"{case.id}: expected {text!r} in the context")
    for text in case.forbidden_content:
        test.assertNotIn(
            text, assembled, f"{case.id}: {text!r} should not be in the context"
        )


class StandinContextAssemblyTests(TestCase):
    """The hand-made stand-in fixtures: proves the harness, runs everywhere."""

    @classmethod
    def setUpTestData(cls):
        STANDIN.load_into_db()


add_case_tests(StandinContextAssemblyTests, STANDIN, "context_assembly", check_context)


@unittest.skipUnless(
    GENERATED.is_ready(),
    "no generated fixtures yet: run rag_chat/eval/generate_fixtures.py with a real OpenAI key",
)
class ContextAssemblyTests(TestCase):
    """Real chunks of the example logs and real query embeddings."""

    @classmethod
    def setUpTestData(cls):
        GENERATED.load_into_db()


add_case_tests(ContextAssemblyTests, GENERATED, "context_assembly", check_context)
