"""
The one place the app talks to OpenAI.

The client is built on first use, not at import time, so importing app code
never needs an API key. Callers catch ``APIError`` (re-exported here) for
failures of the API itself; anything else is a bug and should be raised.
"""

from functools import cache
from typing import Any, BinaryIO, Iterable

import openai
from django.conf import settings
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

APIError = openai.APIError

WHISPER_MODEL = "whisper-1"


@cache
def get_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def transcribe(file: BinaryIO, *, prompt: str | None = None) -> dict:
    """Transcribe English audio with Whisper; returns the verbose_json response as a dict."""
    options: dict[str, Any] = {}
    if prompt:
        options["prompt"] = prompt
    response = get_client().audio.transcriptions.create(
        model=WHISPER_MODEL,
        file=file,
        response_format="verbose_json",
        temperature=0,  # Keep low to reduce hallucinations
        language="en",
        **options,
    )
    return response.model_dump()


def chat_completion(
    messages: Iterable[ChatCompletionMessageParam], *, model: str, **options: Any
):
    """
    Create a chat completion. ``options`` pass through to the API (temperature,
    max_completion_tokens, stream, ...). Returns the SDK's ChatCompletion, or a
    stream of chunks when ``stream=True``.
    """
    return get_client().chat.completions.create(
        model=model, messages=messages, **options
    )


def chat_completion_text(
    messages: Iterable[ChatCompletionMessageParam], *, model: str, **options: Any
) -> str:
    """Create a chat completion and return the first choice's text (stripped)."""
    response = chat_completion(messages, model=model, **options)
    return (response.choices[0].message.content or "").strip()


def embed(text: str, *, model: str | None = None) -> list[float]:
    """Embed one piece of text; defaults to settings.OPENAI_EMBEDDINGS_MODEL."""
    response = get_client().embeddings.create(
        model=model or settings.OPENAI_EMBEDDINGS_MODEL,
        input=text.strip(),
    )
    return response.data[0].embedding
