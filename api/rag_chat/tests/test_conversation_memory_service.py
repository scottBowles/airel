from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import ChatMessage, ChatSession
from ..services.build_conversation_memory import build_conversation_memory


class GetPromptMessagesStrTests(TestCase):
    """Tests for get_prompt_messages_str (orchestrator)."""

    def setUp(self):
        self.user = get_user_model().objects.create(username="testuser")
        self.session = ChatSession.objects.create(
            user=self.user, title="Test Session", conversation_summary=""
        )

    def test_no_messages_returns_empty(self):
        result = build_conversation_memory(self.session, "hello")
        self.assertEqual(result, "")

    def test_includes_recent_messages_under_limit(self):
        ChatMessage.objects.create(
            session=self.session, message="first question", response="first answer"
        )
        ChatMessage.objects.create(
            session=self.session, message="second question", response="second answer"
        )
        result = build_conversation_memory(
            self.session, "new question", max_tokens_before_summary=10000
        )
        self.assertIn("user: first question", result)
        self.assertIn("assistant: first answer", result)
        self.assertIn("user: second question", result)
        self.assertIn("assistant: second answer", result)

    def test_messages_in_chronological_order(self):
        ChatMessage.objects.create(session=self.session, message="first", response="r1")
        ChatMessage.objects.create(
            session=self.session, message="second", response="r2"
        )
        result = build_conversation_memory(
            self.session, "new", max_tokens_before_summary=10000
        )
        first_pos = result.index("user: first")
        second_pos = result.index("user: second")
        self.assertLess(first_pos, second_pos)

    def test_existing_summary_included(self):
        self.session.conversation_summary = "Previously discussed dragons."
        self.session.save()
        result = build_conversation_memory(
            self.session, "new question", max_tokens_before_summary=10000
        )
        self.assertIn("Previously discussed dragons.", result)

    @patch(
        "nucleus.ai.chat_completion_text",
        return_value="Summary of the conversation so far.",
    )
    def test_summarization_triggered_when_over_limit(self, mock_chat):
        # Create enough messages to exceed a very small limit
        for i in range(10):
            ChatMessage.objects.create(
                session=self.session,
                message=f"question {i} with some extra words to use tokens",
                response=f"answer {i} with some extra words to use tokens",
            )

        result = build_conversation_memory(
            self.session,
            "new question",
            max_tokens_before_summary=20,
            target_tokens_after_summary=5,
        )

        # LLM was called to generate summary
        mock_chat.assert_called_once()

        # Summary was persisted to the session
        self.session.refresh_from_db()
        self.assertEqual(
            self.session.conversation_summary,
            "Summary of the conversation so far.",
        )

        # Some messages were marked as included in summary
        summarized_count = ChatMessage.objects.filter(
            session=self.session, included_in_summary=True
        ).count()
        self.assertGreater(summarized_count, 0)

        # Result includes the new summary
        self.assertIn("Summary of the conversation so far.", result)

    @patch("nucleus.ai.chat_completion_text")
    def test_no_llm_call_when_under_limit(self, mock_chat):
        ChatMessage.objects.create(session=self.session, message="hi", response="hello")
        build_conversation_memory(self.session, "new", max_tokens_before_summary=10000)
        mock_chat.assert_not_called()

    def test_already_summarized_messages_excluded(self):
        ChatMessage.objects.create(
            session=self.session,
            message="old question",
            response="old answer",
            included_in_summary=True,
        )
        ChatMessage.objects.create(
            session=self.session, message="new question", response="new answer"
        )
        result = build_conversation_memory(
            self.session, "latest", max_tokens_before_summary=10000
        )
        self.assertNotIn("old question", result)
        self.assertIn("new question", result)
