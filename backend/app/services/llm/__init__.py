"""LLM provider abstraction — public re-exports.

Callers should import from this package, not from submodules.
"""

from app.services.llm.base import (
    Embedder,
    LLMConfigError,
    LLMError,
    LLMInputTooLarge,
    LLMInvalidResponse,
    LLMProvider,
    LLMRateLimited,
    LLMTimeoutError,
)
from app.services.llm.factory import get_embedder, get_llm, reset_for_tests

__all__ = [
    "Embedder",
    "LLMConfigError",
    "LLMError",
    "LLMInputTooLarge",
    "LLMInvalidResponse",
    "LLMProvider",
    "LLMRateLimited",
    "LLMTimeoutError",
    "get_embedder",
    "get_llm",
    "reset_for_tests",
]
