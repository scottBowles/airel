"""
Contract tests for nucleus.ai against the real OpenAI SDK surface.

The client is replaced by an autospec of openai.OpenAI, so calling a method or
argument the installed SDK does not have fails here instead of in production.
"""

import functools
from unittest import TestCase
from unittest.mock import create_autospec, patch

from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from openai.types.audio import TranscriptionVerbose
from openai.types.chat import ChatCompletion

from nucleus import ai


def _autospec(cls, real):
    """
    create_autospec(cls) plus autospecs of its resource attributes.

    create_autospec does not follow functools.cached_property, which is how the
    SDK exposes resources (client.audio, client.chat, ...), so walk them using a
    real instance to learn each resource's class.
    """
    mock = create_autospec(cls, instance=True)
    for name in dir(cls):
        if name.startswith("with_"):
            continue
        attr = next((k.__dict__[name] for k in cls.__mro__ if name in k.__dict__), None)
        if isinstance(attr, functools.cached_property):
            resource = getattr(real, name)
            setattr(mock, name, _autospec(type(resource), resource))
    return mock


def autospec_openai():
    return _autospec(OpenAI, OpenAI(api_key="test"))


class AutospecTests(TestCase):
    def test_autospec_rejects_methods_the_sdk_lacks(self):
        client = autospec_openai()
        with self.assertRaises(AttributeError):
            client.audio.transcribe  # the openai 0.x name; removed in 1.x

    def test_autospec_rejects_unknown_arguments(self):
        client = autospec_openai()
        with self.assertRaises(TypeError):
            client.embeddings.create(model="m", input="x", engine="davinci")


class AiModuleContractTests(TestCase):
    def setUp(self):
        self.client = autospec_openai()
        patcher = patch.object(ai, "get_client", return_value=self.client)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_transcribe(self):
        self.client.audio.transcriptions.create.return_value = (
            TranscriptionVerbose.model_validate(
                {
                    "text": "Hello there.",
                    "language": "english",
                    "duration": 1.5,
                    "segments": [
                        {
                            "id": 0,
                            "seek": 0,
                            "start": 0.0,
                            "end": 1.5,
                            "text": "Hello there.",
                            "tokens": [1, 2],
                            "temperature": 0.0,
                            "avg_logprob": -0.1,
                            "compression_ratio": 1.0,
                            "no_speech_prob": 0.0,
                        }
                    ],
                }
            )
        )
        audio = object()

        result = ai.transcribe(audio, prompt="This is Izar")

        self.client.audio.transcriptions.create.assert_called_once_with(
            model="whisper-1",
            file=audio,
            response_format="verbose_json",
            temperature=0,
            language="en",
            prompt="This is Izar",
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(result["text"], "Hello there.")
        self.assertEqual(result["segments"][0]["end"], 1.5)

    def test_transcribe_without_prompt_omits_it(self):
        self.client.audio.transcriptions.create.return_value = (
            TranscriptionVerbose.model_construct(text="x", language="en", duration=1)
        )

        ai.transcribe(object())

        kwargs = self.client.audio.transcriptions.create.call_args.kwargs
        self.assertNotIn("prompt", kwargs)

    def test_chat_completion_text(self):
        self.client.chat.completions.create.return_value = (
            ChatCompletion.model_validate(
                {
                    "id": "c1",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "gpt-test",
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {"role": "assistant", "content": "  A reply. "},
                        }
                    ],
                }
            )
        )
        messages = [{"role": "user", "content": "Hi"}]

        text = ai.chat_completion_text(messages, model="gpt-test", temperature=0.2)

        self.client.chat.completions.create.assert_called_once_with(
            model="gpt-test", messages=messages, temperature=0.2
        )
        self.assertEqual(text, "A reply.")

    def test_chat_completion_passes_streaming_options(self):
        messages = [{"role": "user", "content": "Hi"}]

        ai.chat_completion(
            messages,
            model="gpt-test",
            max_completion_tokens=10,
            stream=True,
            stream_options={"include_usage": True},
        )

        self.client.chat.completions.create.assert_called_once_with(
            model="gpt-test",
            messages=messages,
            max_completion_tokens=10,
            stream=True,
            stream_options={"include_usage": True},
        )

    def test_embed(self):
        self.client.embeddings.create.return_value = (
            CreateEmbeddingResponse.model_validate(
                {
                    "object": "list",
                    "model": "embed-test",
                    "data": [{"object": "embedding", "index": 0, "embedding": [0.1]}],
                    "usage": {"prompt_tokens": 1, "total_tokens": 1},
                }
            )
        )

        self.assertEqual(ai.embed("  some text \n", model="embed-test"), [0.1])
        self.client.embeddings.create.assert_called_once_with(
            model="embed-test", input="some text"
        )


class ClientConstructionTests(TestCase):
    def setUp(self):
        ai.get_client.cache_clear()
        self.addCleanup(ai.get_client.cache_clear)

    def test_client_is_built_on_first_use_and_reused(self):
        with patch.object(ai, "OpenAI") as openai_cls:
            first = ai.get_client()
            second = ai.get_client()

        openai_cls.assert_called_once()
        self.assertIs(first, second)
