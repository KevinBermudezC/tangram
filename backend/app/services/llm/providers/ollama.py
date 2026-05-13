"""Ollama adapter — local Ollama runtime or Ollama Cloud.

Same SDK and same endpoint shape for both. Cloud usage just needs
`OLLAMA_API_KEY` to be set; it goes in the Authorization header.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import TypeVar

import httpx
from ollama import AsyncClient
from pydantic import BaseModel, ValidationError

from app.schemas.chat import ChatMessage
from app.services.llm.base import (
    LLMConfigError,
    LLMInvalidResponse,
    LLMProviderBase,
    LLMRateLimited,
    LLMTimeoutError,
)

T = TypeVar("T", bound=BaseModel)


class _OllamaBase(LLMProviderBase):
    """Shared Ollama client construction for chat + embedder."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        super().__init__(
            max_input_chars=max_input_chars,
            max_output_tokens=max_output_tokens,
            secrets_to_redact=[api_key] if api_key else [],
        )
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = AsyncClient(host=base_url, headers=headers)


class OllamaProvider(_OllamaBase):
    """Chat / structured / streaming."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        super().__init__(
            base_url=base_url,
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
            response = await self._client.chat(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                options={"temperature": temperature, "num_predict": capped},
            )
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise LLMRateLimited(self._redact(str(e))) from None
            raise
        return response["message"]["content"]

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

        async def _call(strict_messages: list[ChatMessage]) -> str:
            response = await self._client.chat(
                model=self._model,
                messages=[m.model_dump() for m in strict_messages],
                format=schema.model_json_schema(),
                options={"temperature": temperature, "num_predict": capped},
            )
            return response["message"]["content"]

        first = await _call(messages)
        try:
            return schema.model_validate_json(first)
        except ValidationError:
            stricter = [
                *messages,
                ChatMessage(
                    role="user",
                    content=(
                        "Your previous response did not match the required JSON schema. "
                        "Respond again with valid JSON that exactly matches the schema."
                    ),
                ),
            ]
            try:
                second = await _call(stricter)
                return schema.model_validate_json(second)
            except ValidationError as e:
                raise LLMInvalidResponse(
                    f"Ollama returned invalid JSON for schema {schema.__name__} "
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
            async for chunk in await self._client.chat(
                model=self._model,
                messages=[m.model_dump() for m in messages],
                stream=True,
                options={"temperature": temperature, "num_predict": capped},
            ):
                piece = chunk.get("message", {}).get("content", "")
                if piece:
                    yield piece
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(self._redact(str(e))) from None


class OllamaEmbedder(_OllamaBase):
    """Text-to-vector via Ollama's embed endpoint."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None,
        model: str,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        super().__init__(
            base_url=base_url,
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
            response = await self._client.embed(model=self._model, input=texts)
        except httpx.TimeoutException as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except httpx.HTTPStatusError as e:
            raise LLMConfigError(self._redact(str(e))) from None
        # Ollama returns either a single vector or a list under `embeddings`.
        embeddings = response.get("embeddings")
        if embeddings is None:
            single = response.get("embedding")
            if single is None:
                redacted = self._redact(json.dumps(response))
                raise LLMInvalidResponse(f"Ollama embed response missing 'embeddings': {redacted}")
            return [single]
        return embeddings
