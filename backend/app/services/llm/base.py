"""LLM provider abstraction.

This module defines the two protocols every LLM adapter must implement
(`LLMProvider` for chat-style operations, `Embedder` for text-to-vector
embeddings) and the typed error hierarchy that adapters raise.

Operational guardrails (input length cap, output token cap, retry on
transient failures, API-key redaction in error paths) live in
`LLMProviderBase`. Concrete adapters inherit from it.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ValidationError

from app.schemas.chat import ChatMessage

T = TypeVar("T", bound=BaseModel)


# --- Errors ------------------------------------------------------------------


class LLMError(Exception):
    """Base for every error surfaced by the LLM layer."""


class LLMConfigError(LLMError):
    """Misconfiguration — missing key, unsupported provider, bad base URL."""


class LLMTimeoutError(LLMError):
    """The provider did not respond within the configured timeout."""


class LLMInvalidResponse(LLMError):
    """The provider returned content that failed validation, even after retry."""


class LLMRateLimited(LLMError):
    """The provider rate-limited us (HTTP 429 or equivalent)."""


class LLMInputTooLarge(LLMError):
    """Caller-supplied messages exceed the configured input character cap."""


# --- Protocols ---------------------------------------------------------------


@runtime_checkable
class LLMProvider(Protocol):
    """Chat-style operations. Every concrete adapter implements this surface."""

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Return the full text response. No streaming."""

    async def generate_structured(
        self,
        messages: list[ChatMessage],
        schema: type[T],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.3,
    ) -> T:
        """Return an instance of `schema`, validated. Raise on failure."""

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Yield prose chunks as they arrive. Not used for structured outputs."""


@runtime_checkable
class Embedder(Protocol):
    """Text-to-vector embedding. Separate protocol — not every chat provider
    advertises a first-party embedding API (Anthropic does not, at this time)."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text. Order matches input order."""


# --- Shared base for concrete adapters --------------------------------------


class LLMProviderBase:
    """Operational guardrails shared by every adapter.

    Adapters inherit from this and call the helpers. Centralizing here means
    the rules cannot be forgotten in a new adapter.
    """

    def __init__(
        self,
        *,
        max_input_chars: int,
        max_output_tokens: int,
        secrets_to_redact: list[str] | None = None,
    ) -> None:
        self._max_input_chars = max_input_chars
        self._max_output_tokens = max_output_tokens
        # Non-empty key fragments that must never appear in errors or logs.
        self._secrets = [s for s in (secrets_to_redact or []) if s]

    # -- Input / output caps --------------------------------------------------

    def _check_input(self, messages: list[ChatMessage]) -> None:
        total = sum(len(m.content) for m in messages)
        if total > self._max_input_chars:
            raise LLMInputTooLarge(
                f"Input length {total} chars exceeds MAX_INPUT_CHARS={self._max_input_chars}"
            )

    def _apply_caps(self, max_tokens: int | None) -> int:
        if max_tokens is None or max_tokens > self._max_output_tokens:
            return self._max_output_tokens
        return max_tokens

    # -- Validation + retry helper for structured outputs --------------------

    async def _validate_or_retry(
        self,
        schema: type[T],
        first_attempt_text: str,
        retry_callable,
    ) -> T:
        """Try to parse `first_attempt_text` as `schema`. On failure, call
        `retry_callable()` once for a second attempt, then give up."""
        try:
            return schema.model_validate_json(first_attempt_text)
        except ValidationError:
            try:
                second_text = await retry_callable()
                return schema.model_validate_json(second_text)
            except ValidationError as e:
                raise LLMInvalidResponse(
                    f"Provider returned invalid JSON for schema {schema.__name__} "
                    f"after one retry: {self._redact(str(e))}"
                ) from None

    # -- Key redaction --------------------------------------------------------

    def _redact(self, text: str) -> str:
        """Remove any configured secret fragment from `text`."""
        if not self._secrets:
            return text
        # Escape each secret to avoid regex injection issues if a key contains regex metas.
        pattern = re.compile("|".join(re.escape(s) for s in self._secrets))
        return pattern.sub("[REDACTED]", text)
