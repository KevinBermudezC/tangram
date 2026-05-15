from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Tangram"
    app_version: str = "0.1.0"
    environment: Literal["development", "production", "test"] = "development"

    data_dir: Path = Field(
        default=Path("data"),
        description=(
            "Root directory for filesystem-backed storage. Diagrams live in <data_dir>/diagrams/."
        ),
    )
    chroma_path: Path = Field(
        default=Path("data/patterns.chroma"),
        description="Filesystem location of the Chroma vector store for the patterns library.",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description=(
            "Ollama base URL. Use 'https://ollama.com' for Ollama Cloud — requires OLLAMA_API_KEY."
        ),
    )
    ollama_api_key: str | None = Field(
        default=None,
        description="Bearer token for Ollama Cloud. Leave empty for local Ollama.",
    )
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # Chat model per provider. The adapter for the configured LLM_PROVIDER reads
    # its own value. Cross-provider name normalization is not attempted.
    ollama_chat_model: str = "qwen3:4b-instruct"
    openai_chat_model: str = "gpt-4o-mini"
    anthropic_chat_model: str = "claude-haiku-4-5"

    embedder: str = Field(
        default="ollama/nomic-embed-text-v2-moe",
        description="Embedder used to populate the patterns store. Format: 'provider/model'.",
    )

    # User-facing input cap. Used by the HTTP layer to reject oversized
    # `prompt` bodies before any LLM work is done.
    max_input_chars: int = 4000

    # LLM-facing input cap. Used by every LLMProvider adapter against the
    # full composed message list (mode prompt + component summaries +
    # retrieved patterns + rule findings + user prompt). This cap protects
    # against runaway prompt composition; it is NOT a user-input cap.
    max_llm_input_chars: int = 32000

    max_output_tokens: int = 2048


@lru_cache
def get_settings() -> Settings:
    return Settings()
