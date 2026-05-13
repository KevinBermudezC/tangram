"""Schema for the curated patterns library.

Each pattern lives at `patterns/<id>.md` with YAML frontmatter (parsed into the
Pydantic model below) and a markdown body. The body is kept as a string; the
loader does not pre-parse sections (callers do their own extraction).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.schemas.diagram import NodeType


class PatternComplexity(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Pattern(BaseModel):
    """One curated architectural pattern."""

    id: str = Field(description="Kebab-case identifier. Must equal the markdown filename stem.")
    title: str
    complexity: PatternComplexity
    tags: list[str] = Field(
        default_factory=list,
        description="Free-form taxonomy tags.",
    )
    component_types: list[NodeType] = Field(
        description="Which NodeType values appear in this pattern.",
    )
    body: str = Field(
        description="Raw markdown body after the frontmatter block.",
    )

    @field_validator("id")
    @classmethod
    def _id_is_kebab_case(cls, v: str) -> str:
        if not v or not v.replace("-", "").isalnum() or v != v.lower():
            raise ValueError("id must be lowercase kebab-case (letters, digits, hyphens only)")
        return v

    @field_validator("title", "body")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must be non-empty")
        return v

    @field_validator("component_types")
    @classmethod
    def _component_types_non_empty(cls, v: list[NodeType]) -> list[NodeType]:
        if not v:
            raise ValueError("must list at least one component type")
        return v
