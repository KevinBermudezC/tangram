"""Operational guardrails enforced before any network call.

These tests construct adapters with low caps and verify that oversized inputs
raise before any SDK method is invoked.
"""

from __future__ import annotations

import pytest

from app.schemas.chat import ChatMessage
from app.services.llm import LLMInputTooLarge
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.ollama import OllamaProvider
from app.services.llm.providers.openai import OpenAIProvider


def _oversized_messages(total_chars: int = 5000) -> list[ChatMessage]:
    return [ChatMessage(role="user", content="x" * total_chars)]


@pytest.mark.asyncio
async def test_ollama_rejects_oversized_input() -> None:
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        api_key=None,
        model="qwen3:4b-instruct",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    with pytest.raises(LLMInputTooLarge):
        await provider.generate(_oversized_messages())


@pytest.mark.asyncio
async def test_openai_rejects_oversized_input() -> None:
    provider = OpenAIProvider(
        api_key="sk-test",
        model="gpt-4o-mini",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    with pytest.raises(LLMInputTooLarge):
        await provider.generate(_oversized_messages())


@pytest.mark.asyncio
async def test_anthropic_rejects_oversized_input() -> None:
    provider = AnthropicProvider(
        api_key="sk-test",
        model="claude-haiku-4-5",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    with pytest.raises(LLMInputTooLarge):
        await provider.generate(_oversized_messages())


def test_apply_caps_clamps_max_tokens() -> None:
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        api_key=None,
        model="qwen3:4b-instruct",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    assert provider._apply_caps(10_000) == 2048
    assert provider._apply_caps(1024) == 1024
    assert provider._apply_caps(None) == 2048
