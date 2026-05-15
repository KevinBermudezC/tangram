"""Schema for LLM modes (personas).

A mode is a markdown file under `modes/` with frontmatter (id, title, summary)
and a body that is the literal system prompt. MVP ships one mode: tutor.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Mode(BaseModel):
    """One LLM persona."""

    id: str = Field(description="Kebab-case identifier. Must equal the filename stem.")
    title: str = Field(description="Human-readable name.")
    summary: str = Field(description="One-line description of the persona.")
    system_prompt: str = Field(
        description="The literal system prompt content (the markdown body of the mode file).",
    )

    @field_validator("id")
    @classmethod
    def _id_kebab_case(cls, v: str) -> str:
        if not v or not v.replace("-", "").isalnum() or v != v.lower():
            raise ValueError("id must be lowercase kebab-case (letters, digits, hyphens only)")
        return v

    @field_validator("title", "summary", "system_prompt")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must be non-empty")
        return v
