"""Factory wires the right adapter for each LLM_PROVIDER and EMBEDDER value.

No live LLM calls — these tests only check that the factory returns the correct
class type based on configuration. Adapter constructors do enough to validate
configuration without making network calls.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.services.llm import LLMConfigError, get_embedder, get_llm, reset_for_tests
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.ollama import OllamaEmbedder, OllamaProvider
from app.services.llm.providers.openai import OpenAIEmbedder, OpenAIProvider


@pytest.fixture(autouse=True)
def _reset_settings_and_cache(monkeypatch: pytest.MonkeyPatch):
    """Each test gets a fresh Settings and a cleared factory cache."""
    reset_for_tests()
    get_settings.cache_clear()
    yield
    reset_for_tests()
    get_settings.cache_clear()


def _configure(monkeypatch: pytest.MonkeyPatch, **overrides) -> None:
    """Patch env vars for a Settings instance."""
    defaults = {
        "LLM_PROVIDER": "ollama",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_API_KEY": "",
        "OPENAI_API_KEY": "sk-test-openai",
        "ANTHROPIC_API_KEY": "sk-test-anthropic",
        "EMBEDDER": "ollama/nomic-embed-text-v2-moe",
        "OLLAMA_CHAT_MODEL": "qwen3:4b-instruct",
        "OPENAI_CHAT_MODEL": "gpt-4o-mini",
        "ANTHROPIC_CHAT_MODEL": "claude-haiku-4-5",
    }
    defaults.update(overrides)
    for k, v in defaults.items():
        monkeypatch.setenv(k, v)


def test_llm_provider_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, LLM_PROVIDER="ollama")
    assert isinstance(get_llm(), OllamaProvider)


def test_llm_provider_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, LLM_PROVIDER="openai")
    assert isinstance(get_llm(), OpenAIProvider)


def test_llm_provider_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, LLM_PROVIDER="anthropic")
    assert isinstance(get_llm(), AnthropicProvider)


def test_llm_provider_unknown_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # Pydantic Settings rejects an out-of-Literal value at construction.
    _configure(monkeypatch, LLM_PROVIDER="mistral")
    with pytest.raises(ValidationError):
        Settings()


def test_openai_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, LLM_PROVIDER="openai", OPENAI_API_KEY="")
    with pytest.raises(LLMConfigError):
        get_llm()


def test_anthropic_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, LLM_PROVIDER="anthropic", ANTHROPIC_API_KEY="")
    with pytest.raises(LLMConfigError):
        get_llm()


def test_embedder_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="ollama/nomic-embed-text-v2-moe")
    assert isinstance(get_embedder(), OllamaEmbedder)


def test_embedder_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="openai/text-embedding-3-small")
    assert isinstance(get_embedder(), OpenAIEmbedder)


def test_embedder_anthropic_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="anthropic/whatever")
    with pytest.raises(LLMConfigError):
        get_embedder()


def test_embedder_malformed_value_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="just-a-model-name")
    with pytest.raises(LLMConfigError):
        get_embedder()


def test_embedder_empty_provider_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="/model-only")
    with pytest.raises(LLMConfigError):
        get_embedder()


def test_embedder_unknown_provider_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _configure(monkeypatch, EMBEDDER="mistral/embed-large")
    with pytest.raises(LLMConfigError):
        get_embedder()
