"""FakeLLMProvider for tests.

Returns predetermined structured outputs or raises predetermined exceptions.
Protocol-compatible with `app.services.llm.LLMProvider`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypeVar

from pydantic import BaseModel

from app.schemas.chat import ChatMessage, ChatStreamPart

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    """LLM provider stand-in for tests.

    - `structured_response`: what `generate_structured` returns.
    - `structured_error`: exception to raise instead of returning.
    - `stream_script`: one list of parts per `stream_parts` call (tool loop).
    """

    def __init__(
        self,
        structured_response: Any = None,
        structured_error: Exception | None = None,
        text_response: str = "ok",
        stream_script: list[list[ChatStreamPart]] | None = None,
    ) -> None:
        self.structured_response = structured_response
        self.structured_error = structured_error
        self.text_response = text_response
        self.stream_script = stream_script
        self._script_i = 0
        self.calls: list[tuple[list[ChatMessage], type[BaseModel] | None]] = []
        self.stream_tools: list[dict[str, Any]] | None = None

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        self.calls.append((list(messages), None))
        if self.structured_error is not None:
            raise self.structured_error
        return self.text_response

    async def generate_structured(
        self,
        messages: list[ChatMessage],
        schema: type[T],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.3,
    ) -> T:
        self.calls.append((list(messages), schema))
        if self.structured_error is not None:
            raise self.structured_error
        if isinstance(self.structured_response, schema):
            return self.structured_response
        return schema.model_validate(self.structured_response)

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        return _yield_once(self._text_or_raise(messages))

    def stream_parts(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[ChatStreamPart]:
        self.stream_tools = tools
        return _yield_parts(self, messages)

    def _text_or_raise(self, messages: list[ChatMessage]) -> str:
        self.calls.append((list(messages), None))
        if self.structured_error is not None:
            raise self.structured_error
        return self.text_response


async def _yield_once(text: str) -> AsyncIterator[str]:
    yield text


async def _yield_parts(
    provider: FakeLLMProvider, messages: list[ChatMessage]
) -> AsyncIterator[ChatStreamPart]:
    if provider.stream_script is not None:
        provider.calls.append((list(messages), None))
        if provider.structured_error is not None:
            raise provider.structured_error
        if provider._script_i >= len(provider.stream_script):
            return
        parts = provider.stream_script[provider._script_i]
        provider._script_i += 1
        for part in parts:
            yield part
        return
    text = provider._text_or_raise(messages)
    if text:
        yield ChatStreamPart(type="text", text=text)
