"""Every adapter implements the protocol's full surface.

Uses `runtime_checkable` Protocols + `isinstance` to verify each concrete class
satisfies the contract. No live LLM calls.
"""

from __future__ import annotations

from app.services.llm.base import Embedder, LLMProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.ollama import OllamaEmbedder, OllamaProvider
from app.services.llm.providers.openai import OpenAIEmbedder, OpenAIProvider


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
