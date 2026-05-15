"""Application settings.

Every operational value comes from environment variables (or a `.env` file
loaded via `pydantic-settings`). No defaults live in this file. The canonical
list of variables with their suggested values lives in `backend/.env.example`;
new contributors `cp .env.example .env` and edit.

API keys are the only optional fields. Each user only fills in the key for
the provider they actually use; the others stay empty.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App metadata --------------------------------------------------------

    app_name: str
    app_version: str
    environment: Literal["development", "production", "test"]

    # --- Filesystem layout ---------------------------------------------------

    data_dir: Path
    chroma_path: Path

    # --- HTTP ----------------------------------------------------------------

    cors_origins: list[str]

    # --- LLM provider selection ---------------------------------------------

    llm_provider: Literal["ollama", "openai", "anthropic"]

    # Ollama (local or cloud)
    ollama_base_url: str
    ollama_api_key: str = ""  # empty for local Ollama; required for Ollama Cloud
    ollama_chat_model: str

    # OpenAI (BYOK)
    openai_api_key: str = ""  # only required if LLM_PROVIDER=openai
    openai_chat_model: str

    # Anthropic (BYOK)
    anthropic_api_key: str = ""  # only required if LLM_PROVIDER=anthropic
    anthropic_chat_model: str

    # Embedder routing — independent of LLM_PROVIDER. Format: "<provider>/<model>".
    embedder: str

    # --- Operational guardrails ---------------------------------------------

    # Hard cap on the user-supplied `prompt` field at the HTTP layer.
    max_input_chars: int

    # Hard cap on the full composed message list sent to the LLM. Distinct from
    # max_input_chars; protects against runaway prompt composition, not user
    # input.
    max_llm_input_chars: int

    max_output_tokens: int


@lru_cache
def get_settings() -> Settings:
    return Settings()
