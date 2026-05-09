from functools import lru_cache
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

    database_url: str = Field(
        default="postgresql+psycopg://tangram:tangram@localhost:5432/tangram",
        description="Postgres connection string. Override via DATABASE_URL.",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    llm_provider: Literal["ollama", "openai", "anthropic"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    max_input_chars: int = 4000
    max_output_tokens: int = 2048


@lru_cache
def get_settings() -> Settings:
    return Settings()
