"""Shared pytest configuration.

`config.py` has no Python-level defaults — every Settings field comes from
the environment. Without help, every test that constructs Settings (directly
or transitively via get_settings) would fail with "missing field" errors.

We set env vars at *module load* via `os.environ.setdefault`, BEFORE pytest
imports test modules (which may transitively import `app.main` → call
`get_settings()` → instantiate Settings at collection time). Individual
tests can still monkeypatch specific values to exercise edge cases.
"""

from __future__ import annotations

import os

import pytest

from app.core.config import get_settings

TEST_ENV_DEFAULTS: dict[str, str] = {
    # App metadata
    "APP_NAME": "Tangram",
    "APP_VERSION": "0.1.0",
    "ENVIRONMENT": "test",
    # Filesystem
    "DATA_DIR": "data",
    "CHROMA_PATH": "data/patterns.chroma",
    # HTTP
    "CORS_ORIGINS": '["http://localhost:3000"]',
    # LLM provider
    "LLM_PROVIDER": "ollama",
    # Ollama
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_API_KEY": "",
    "OLLAMA_CHAT_MODEL": "qwen3:4b-instruct",
    # OpenAI
    "OPENAI_API_KEY": "sk-test-openai",
    "OPENAI_CHAT_MODEL": "gpt-4o-mini",
    # Anthropic
    "ANTHROPIC_API_KEY": "sk-test-anthropic",
    "ANTHROPIC_CHAT_MODEL": "claude-haiku-4-5",
    # Embedder
    "EMBEDDER": "ollama/nomic-embed-text-v2-moe",
    # Guardrails
    "MAX_INPUT_CHARS": "4000",
    "MAX_LLM_INPUT_CHARS": "32000",
    "MAX_OUTPUT_TOKENS": "2048",
}


# Module-level: applies before test modules are imported. Uses setdefault so
# values already present in the environment (e.g. a developer's local .env)
# are NOT overridden.
for _key, _value in TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)


@pytest.fixture(autouse=True)
def _isolate_settings_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Re-assert test defaults per test and clear the Settings cache.

    monkeypatch.setenv is reverted between tests, so any test that overrode a
    value gets the test default back here. The cache clear ensures
    `get_settings()` re-reads the environment.
    """
    for key, value in TEST_ENV_DEFAULTS.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
