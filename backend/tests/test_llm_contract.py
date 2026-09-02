"""Every adapter implements the protocol's full surface.

Uses `runtime_checkable` Protocols + `isinstance` to verify each concrete class
satisfies the contract. No live LLM calls.
"""

from __future__ import annotations

import inspect

from app.schemas.chat import ChatMessage, ChatStreamPart
from app.services.llm.base import Embedder, LLMProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.ollama import OllamaEmbedder, OllamaProvider
from app.services.llm.providers.openai import OpenAIEmbedder, OpenAIProvider
from tests._fake_llm import FakeLLMProvider


def _make_ollama_provider() -> OllamaProvider:
    return OllamaProvider(
        base_url="http://localhost:11434",
        api_key=None,
        model="qwen3:4b-instruct",
        max_input_chars=4000,
        max_output_tokens=2048,
    )


def _make_ollama_embedder() -> OllamaEmbedder:
    return OllamaEmbedder(
        base_url="http://localhost:11434",
        api_key=None,
        model="nomic-embed-text-v2-moe",
        max_input_chars=4000,
        max_output_tokens=2048,
    )


def _make_openai_provider() -> OpenAIProvider:
    return OpenAIProvider(
        api_key="sk-test",
        model="gpt-4o-mini",
        max_input_chars=4000,
        max_output_tokens=2048,
    )


def _make_openai_embedder() -> OpenAIEmbedder:
    return OpenAIEmbedder(
        api_key="sk-test",
        model="text-embedding-3-small",
        max_input_chars=4000,
        max_output_tokens=2048,
    )


def _make_anthropic_provider() -> AnthropicProvider:
    return AnthropicProvider(
        api_key="sk-test",
        model="claude-haiku-4-5",
        max_input_chars=4000,
        max_output_tokens=2048,
    )


def test_ollama_provider_implements_llm_protocol() -> None:
    assert isinstance(_make_ollama_provider(), LLMProvider)


def test_openai_provider_implements_llm_protocol() -> None:
    assert isinstance(_make_openai_provider(), LLMProvider)


def test_anthropic_provider_implements_llm_protocol() -> None:
    assert isinstance(_make_anthropic_provider(), LLMProvider)


def test_ollama_embedder_implements_embedder_protocol() -> None:
    assert isinstance(_make_ollama_embedder(), Embedder)


def test_openai_embedder_implements_embedder_protocol() -> None:
    assert isinstance(_make_openai_embedder(), Embedder)


def test_providers_expose_stream_parts_with_tools() -> None:
    for maker in (_make_ollama_provider, _make_openai_provider, _make_anthropic_provider):
        provider = maker()
        assert isinstance(provider, LLMProvider)
        sig = inspect.signature(provider.stream_parts)
        assert "tools" in sig.parameters


def test_fake_llm_implements_llm_protocol() -> None:
    assert isinstance(FakeLLMProvider(), LLMProvider)


async def test_fake_stream_parts_text_only_matches_stream() -> None:
    fake = FakeLLMProvider(text_response="hello")
    messages = [ChatMessage(role="user", content="hi")]
    streamed: list[str] = []
    async for chunk in fake.stream(messages):
        streamed.append(chunk)
    fake_parts = FakeLLMProvider(text_response="hello")
    parts: list[ChatStreamPart] = []
    async for part in fake_parts.stream_parts(messages):
        parts.append(part)
    assert parts
    assert all(p.type == "text" for p in parts)
    assert "".join(p.text or "" for p in parts) == "".join(streamed)


async def test_fake_stream_parts_script_yields_tool_then_text() -> None:
    fake = FakeLLMProvider(
        stream_script=[
            [
                ChatStreamPart(
                    type="tool-call",
                    tool_call_id="call_1",
                    tool_name="inspect_node",
                    arguments='{"node_id":"orders"}',
                )
            ],
            [ChatStreamPart(type="text", text="Orders sits between API and Worker.")],
        ]
    )
    messages = [ChatMessage(role="user", content="why?")]
    first = [p async for p in fake.stream_parts(messages, tools=[{"type": "function"}])]
    assert first[0].type == "tool-call"
    assert first[0].tool_name == "inspect_node"
    assert first[0].tool_call_id == "call_1"
    second = [p async for p in fake.stream_parts(messages, tools=[{"type": "function"}])]
    assert second[0].type == "text"
    assert "Orders" in (second[0].text or "")
