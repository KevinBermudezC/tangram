"""OpenAI adapter."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, TypeVar

from openai import APITimeoutError as _APITimeoutError
from openai import AsyncOpenAI
from openai import RateLimitError as _RateLimitError
from pydantic import BaseModel

from app.schemas.chat import ChatMessage, ChatStreamPart
from app.services.llm.base import (
    LLMConfigError,
    LLMInvalidResponse,
    LLMProviderBase,
    LLMRateLimited,
    LLMTimeoutError,
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
                messages=[m.model_dump(exclude_none=True) for m in messages],
                max_completion_tokens=capped,
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
        """Use OpenAI's parse() helper.

        Why `parse()` instead of `create(response_format=...)`: OpenAI's
        strict mode requires `additionalProperties: false` on every object,
        every field listed under `required`, no defaults, no format
        annotations. Pydantic's `model_json_schema()` doesn't produce that
        dialect. The SDK's `parse()` helper does the munging for us and
        returns a parsed Pydantic instance directly.
        """
        self._check_input(messages)
        capped = self._apply_caps(max_tokens)
        try:
            response = await self._client.chat.completions.parse(
                model=self._model,
                messages=[m.model_dump(exclude_none=True) for m in messages],
                max_completion_tokens=capped,
                temperature=temperature,
                response_format=schema,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None

        message = response.choices[0].message

        # `refusal` is OpenAI's safety mechanism for prompts they refuse to
        # answer; surface it as an invalid response.
        if getattr(message, "refusal", None):
            raise LLMInvalidResponse(
                f"OpenAI refused the request for schema {schema.__name__}: "
                f"{self._redact(message.refusal)}"
            )

        parsed = getattr(message, "parsed", None)
        if parsed is None:
            raise LLMInvalidResponse(
                f"OpenAI returned no parsed content for schema {schema.__name__}"
            )
        return parsed

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
                messages=[m.model_dump(exclude_none=True) for m in messages],
                max_completion_tokens=capped,
                temperature=temperature,
                stream=True,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        async for chunk in stream:
            piece = chunk.choices[0].delta.content
            if piece:
                yield piece

    async def stream_parts(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[ChatStreamPart]:
        if not tools:
            async for text in self.stream(messages, max_tokens=max_tokens, temperature=temperature):
                if text:
                    yield ChatStreamPart(type="text", text=text)
            return

        self._check_input(messages)
        capped = self._apply_caps(max_tokens)
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=_to_openai_messages(messages),
                max_completion_tokens=capped,
                temperature=temperature,
                tools=tools,
                stream=True,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None

        pending: dict[int, dict[str, str]] = {}
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield ChatStreamPart(type="text", text=delta.content)
            for tc in delta.tool_calls or []:
                slot = pending.setdefault(tc.index, {"id": "", "name": "", "arguments": ""})
                if tc.id:
                    slot["id"] = tc.id
                if tc.function is not None:
                    if tc.function.name:
                        slot["name"] = tc.function.name
                    if tc.function.arguments:
                        slot["arguments"] += tc.function.arguments
        for slot in pending.values():
            yield ChatStreamPart(
                type="tool-call",
                tool_call_id=slot["id"] or "call_0",
                tool_name=slot["name"],
                arguments=slot["arguments"] or "{}",
            )


def _to_openai_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """Map ChatMessage (including tool turns) to OpenAI's wire shape."""
    out: list[dict[str, Any]] = []
    for m in messages:
        item: dict[str, Any] = {"role": m.role}
        if m.role == "tool":
            item["content"] = m.content
            if m.tool_call_id:
                item["tool_call_id"] = m.tool_call_id
        elif m.tool_calls:
            item["content"] = m.content or None
            item["tool_calls"] = m.tool_calls
        else:
            item["content"] = m.content
        out.append(item)
    return out


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
