"""Factories for LLM providers and embedders.

Both return cached singletons. Configuration lives in `app.core.config.Settings`.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.services.llm.base import Embedder, LLMConfigError, LLMProvider
from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.ollama import OllamaEmbedder, OllamaProvider
from app.services.llm.providers.openai import OpenAIEmbedder, OpenAIProvider


@lru_cache
def get_llm() -> LLMProvider:
    s = get_settings()
    if s.llm_provider == "ollama":
        return OllamaProvider(
            base_url=s.ollama_base_url,
            api_key=s.ollama_api_key,
            model=s.ollama_chat_model,
            max_input_chars=s.max_llm_input_chars,
            max_output_tokens=s.max_output_tokens,
        )
    if s.llm_provider == "openai":
        return OpenAIProvider(
            api_key=s.openai_api_key,
            model=s.openai_chat_model,
            max_input_chars=s.max_llm_input_chars,
            max_output_tokens=s.max_output_tokens,
        )
    if s.llm_provider == "anthropic":
        return AnthropicProvider(
            api_key=s.anthropic_api_key,
            model=s.anthropic_chat_model,
            max_input_chars=s.max_llm_input_chars,
            max_output_tokens=s.max_output_tokens,
        )
    raise LLMConfigError(
        f"Unsupported LLM_PROVIDER={s.llm_provider!r}. Supported: ollama, openai, anthropic."
    )


@lru_cache
def get_embedder() -> Embedder:
    s = get_settings()
    if "/" not in s.embedder:
        raise LLMConfigError(
            f"EMBEDDER must be of the form '<provider>/<model>', got {s.embedder!r}"
        )
    provider, _, model = s.embedder.partition("/")
    if not provider or not model:
        raise LLMConfigError(
            f"EMBEDDER must be of the form '<provider>/<model>', got {s.embedder!r}"
        )

    if provider == "ollama":
        return OllamaEmbedder(
            base_url=s.ollama_base_url,
            api_key=s.ollama_api_key,
            model=model,
            max_input_chars=s.max_llm_input_chars,
            max_output_tokens=s.max_output_tokens,
        )
    if provider == "openai":
        return OpenAIEmbedder(
            api_key=s.openai_api_key,
            model=model,
            max_input_chars=s.max_llm_input_chars,
            max_output_tokens=s.max_output_tokens,
        )
    if provider == "anthropic":
        raise LLMConfigError(
            "Anthropic does not provide a first-party embedding API. "
            "Use ollama/<model> or openai/<model> for EMBEDDER."
        )
    raise LLMConfigError(
        f"Unsupported embedder provider {provider!r} in EMBEDDER={s.embedder!r}. "
        "Supported providers: ollama, openai."
    )


def reset_for_tests() -> None:
    """Drop cached singletons. Tests call this between cases."""
    get_llm.cache_clear()
    get_embedder.cache_clear()
