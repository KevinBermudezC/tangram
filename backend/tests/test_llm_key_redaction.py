"""API keys must never leak into error messages."""

from __future__ import annotations

from app.services.llm.providers.anthropic import AnthropicProvider
from app.services.llm.providers.openai import OpenAIProvider


def test_openai_redacts_key_in_error_text() -> None:
    secret = "sk-redact-me-12345"
    provider = OpenAIProvider(
        api_key=secret,
        model="gpt-4o-mini",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    polluted = f"some error mentioning {secret} in the message"
    redacted = provider._redact(polluted)
    assert secret not in redacted
    assert "[REDACTED]" in redacted


def test_anthropic_redacts_key_in_error_text() -> None:
    secret = "sk-ant-redact-this-12345"
    provider = AnthropicProvider(
        api_key=secret,
        model="claude-haiku-4-5",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    polluted = f"error: {secret} appeared"
    redacted = provider._redact(polluted)
    assert secret not in redacted
    assert "[REDACTED]" in redacted


def test_redact_is_noop_when_no_secrets_configured() -> None:
    # Construct with no api key — secrets list ends up empty
    from app.services.llm.providers.ollama import OllamaProvider

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        api_key=None,
        model="qwen3:4b-instruct",
        max_input_chars=4000,
        max_output_tokens=2048,
    )
    text = "some unrelated error message"
    assert provider._redact(text) == text
