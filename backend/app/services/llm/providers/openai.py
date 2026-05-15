"""OpenAI adapter."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TypeVar

from openai import APITimeoutError as _APITimeoutError
from openai import AsyncOpenAI
from openai import RateLimitError as _RateLimitError
from pydantic import BaseModel, ValidationError

from app.schemas.chat import ChatMessage
from app.services.llm.base import (
    LLMConfigError,
    LLMInvalidResponse,
    LLMProviderBase,
    LLMRateLimited,
    LLMTimeoutError,
    strip_markdown_fence,
)

T = TypeVar("T", bound=BaseModel)


class _OpenAIBase(LLMProviderBase):
    def __init__(
        self,
        *,
        api_key: str | None,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        if not api_key:
            raise LLMConfigError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        super().__init__(
            max_input_chars=max_input_chars,
            max_output_tokens=max_output_tokens,
            secrets_to_redact=[api_key],
        )
        self._client = AsyncOpenAI(api_key=api_key)


class OpenAIProvider(_OpenAIBase):
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        super().__init__(
            api_key=api_key,
            max_input_chars=max_input_chars,
            max_output_tokens=max_output_tokens,
        )
        self._model = model

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        self._check_input(messages)
        capped = self._apply_caps(max_tokens)
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                max_tokens=capped,
                temperature=temperature,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None
        return response.choices[0].message.content or ""

    async def generate_structured(
        self,
        messages: list[ChatMessage],
        schema: type[T],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.3,
    ) -> T:
        self._check_input(messages)
        capped = self._apply_caps(max_tokens)
        schema_payload = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema(),
                "strict": True,
            },
        }

        async def _call() -> str:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                max_tokens=capped,
                temperature=temperature,
                response_format=schema_payload,
            )
            return response.choices[0].message.content or ""

        first = strip_markdown_fence(await _call())
        try:
            return schema.model_validate_json(first)
        except ValidationError:
            # OpenAI's strict JSON Schema mode should never produce invalid JSON;
            # if it does, one retry, then fail.
            try:
                second = strip_markdown_fence(await _call())
                return schema.model_validate_json(second)
            except ValidationError as e:
                raise LLMInvalidResponse(
                    f"OpenAI returned invalid JSON for schema {schema.__name__} "
                    f"after retry: {self._redact(str(e))}"
                ) from None

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        self._check_input(messages)
        capped = self._apply_caps(max_tokens)
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                max_tokens=capped,
                temperature=temperature,
                stream=True,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        async for chunk in stream:
            piece = chunk.choices[0].delta.content
            if piece:
                yield piece


class OpenAIEmbedder(_OpenAIBase):
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        super().__init__(
            api_key=api_key,
            max_input_chars=max_input_chars,
            max_output_tokens=max_output_tokens,
        )
        self._model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        total = sum(len(t) for t in texts)
        if total > self._max_input_chars:
            from app.services.llm.base import LLMInputTooLarge

            raise LLMInputTooLarge(
                f"Embedding input {total} chars exceeds MAX_INPUT_CHARS={self._max_input_chars}"
            )
        try:
            response = await self._client.embeddings.create(model=self._model, input=texts)
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None
        # Preserve input order
        ordered = sorted(response.data, key=lambda d: d.index)
        return [d.embedding for d in ordered]
