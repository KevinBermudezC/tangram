"""FakeLLMProvider for tests.

Returns predetermined structured outputs or raises predetermined exceptions.
Protocol-compatible with `app.services.llm.LLMProvider`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypeVar

from pydantic import BaseModel

from app.schemas.chat import ChatMessage

T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider:
    """LLM provider stand-in for tests.

    - `structured_response`: what `generate_structured` returns. Either a
      Pydantic instance or a dict that the schema will validate.
    - `structured_error`: exception to raise instead of returning.
    """

    def __init__(
        self,
        structured_response: Any = None,
        structured_error: Exception | None = None,
        text_response: str = "ok",
    ) -> None:
        self.structured_response = structured_response
        self.structured_error = structured_error
        self.text_response = text_response
        self.calls: list[tuple[list[ChatMessage], type[BaseModel] | None]] = []

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        self.calls.append((messages, None))
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
        self.calls.append((messages, schema))
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
        return _yield_once(self.text_response)


async def _yield_once(text: str) -> AsyncIterator[str]:
    yield text
