"""Anthropic adapter.

Structured outputs are produced via tool use: we define a single tool whose
input_schema is the requested Pydantic JSON Schema and force the model to call it.
Anthropic does not currently provide a first-party embedding API, so no
AnthropicEmbedder exists — the factory will reject `EMBEDDER=anthropic/*`.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, TypeVar

from anthropic import APITimeoutError as _APITimeoutError
from anthropic import AsyncAnthropic
from anthropic import RateLimitError as _RateLimitError
from pydantic import BaseModel, ValidationError

from app.schemas.chat import ChatMessage, ChatStreamPart
from app.services.llm.base import (
    LLMConfigError,
    LLMInvalidResponse,
    LLMProviderBase,
    LLMRateLimited,
    LLMTimeoutError,
)

T = TypeVar("T", bound=BaseModel)


def _split_system(messages: list[ChatMessage]) -> tuple[str | None, list[dict]]:
    """Anthropic takes a single `system` argument and a list of non-system messages."""
    system_parts: list[str] = []
    rest: list[dict] = []
    pending_tool_results: list[dict] = []

    def flush_tool_results() -> None:
        nonlocal pending_tool_results
        if pending_tool_results:
            rest.append({"role": "user", "content": pending_tool_results})
            pending_tool_results = []

    for m in messages:
        if m.role == "system":
            flush_tool_results()
            system_parts.append(m.content)
            continue
        if m.role == "tool":
            pending_tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": m.tool_call_id or "",
                    "content": m.content,
                }
            )
            continue
        flush_tool_results()
        if m.role == "assistant" and m.tool_calls:
            blocks: list[dict[str, Any]] = []
            if m.content:
                blocks.append({"type": "text", "text": m.content})
            for tc in m.tool_calls:
                fn = tc.get("function") or tc
                raw_args = fn.get("arguments", "{}")
                if isinstance(raw_args, str):
                    try:
                        parsed = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        parsed = {}
                else:
                    parsed = raw_args
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc.get("id") or fn.get("id") or "",
                        "name": fn.get("name") or tc.get("name") or "",
                        "input": parsed,
                    }
                )
            rest.append({"role": "assistant", "content": blocks})
        else:
            rest.append({"role": m.role, "content": m.content})
    flush_tool_results()
    system = "\n\n".join(system_parts) if system_parts else None
    return system, rest


def _openai_tools_to_anthropic(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for t in tools:
        fn = t.get("function") or t
        converted.append(
            {
                "name": fn.get("name") or t.get("name") or "",
                "description": fn.get("description") or t.get("description") or "",
                "input_schema": fn.get("parameters") or t.get("input_schema") or {"type": "object"},
            }
        )
    return converted


class AnthropicProvider(LLMProviderBase):
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        max_input_chars: int,
        max_output_tokens: int,
    ) -> None:
        if not api_key:
            raise LLMConfigError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        super().__init__(
            max_input_chars=max_input_chars,
            max_output_tokens=max_output_tokens,
            secrets_to_redact=[api_key],
        )
        self._client = AsyncAnthropic(api_key=api_key)
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
        system, rest = _split_system(messages)
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=capped,
                temperature=temperature,
                system=system or "",
                messages=rest,
            )
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None
        text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        return "".join(text_blocks)

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
        system, rest = _split_system(messages)

        tool_name = f"emit_{schema.__name__.lower()}"
        tool_definition = {
            "name": tool_name,
            "description": f"Emit a single valid {schema.__name__} object.",
            "input_schema": schema.model_json_schema(),
        }

        async def _call(extra_messages: list[dict] | None = None) -> dict:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=capped,
                temperature=temperature,
                system=system or "",
                messages=rest + (extra_messages or []),
                tools=[tool_definition],
                tool_choice={"type": "tool", "name": tool_name},
            )
            for block in response.content:
                if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                    return block.input
            raise LLMInvalidResponse(
                f"Anthropic did not call tool {tool_name}; response blocks: "
                f"{[getattr(b, 'type', None) for b in response.content]}"
            )

        first = await _call()
        try:
            return schema.model_validate(first)
        except ValidationError:
            try:
                second = await _call(
                    [
                        {
                            "role": "user",
                            "content": (
                                "Your previous tool call did not match the schema. "
                                "Call the tool again with arguments that exactly match the schema."
                            ),
                        }
                    ]
                )
                return schema.model_validate(second)
            except ValidationError as e:
                raise LLMInvalidResponse(
                    f"Anthropic returned invalid tool arguments for {schema.__name__} "
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
        system, rest = _split_system(messages)
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=capped,
                temperature=temperature,
                system=system or "",
                messages=rest,
            ) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield text
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None

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
        system, rest = _split_system(messages)
        current_tool: dict[str, str] | None = None
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=capped,
                temperature=temperature,
                system=system or "",
                messages=rest,
                tools=_openai_tools_to_anthropic(tools),
            ) as stream:
                async for event in stream:
                    etype = getattr(event, "type", None)
                    if etype == "content_block_start":
                        block = getattr(event, "content_block", None)
                        if getattr(block, "type", None) == "tool_use":
                            current_tool = {
                                "id": getattr(block, "id", "") or "",
                                "name": getattr(block, "name", "") or "",
                                "arguments": "",
                            }
                    elif etype == "content_block_delta":
                        delta = getattr(event, "delta", None)
                        dtype = getattr(delta, "type", None)
                        if dtype == "text_delta" and getattr(delta, "text", None):
                            yield ChatStreamPart(type="text", text=delta.text)
                        elif dtype == "input_json_delta" and current_tool is not None:
                            current_tool["arguments"] += getattr(delta, "partial_json", "") or ""
                    elif etype == "content_block_stop" and current_tool is not None:
                        yield ChatStreamPart(
                            type="tool-call",
                            tool_call_id=current_tool["id"] or "call_anthropic",
                            tool_name=current_tool["name"],
                            arguments=current_tool["arguments"] or "{}",
                        )
                        current_tool = None
        except _APITimeoutError as e:
            raise LLMTimeoutError(self._redact(str(e))) from None
        except _RateLimitError as e:
            raise LLMRateLimited(self._redact(str(e))) from None
