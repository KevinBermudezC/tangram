"""Schema for the curated component metadata library.

One `ComponentMetadata` instance per node type. The corresponding YAML files
live at `components/<type>.yaml` at the repo root and are loaded by
`app.services.components.loader`.

Required string / list fields are validated as non-empty so a contributor
cannot ship a YAML with `description: ""` or `tradeoffs: []` that silently
passes validation but provides no value.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas.diagram import NodeType


def _non_empty_str(value: str) -> str:
    if not value or not value.strip():
        raise ValueError("must be a non-empty string")
    return value


def _non_empty_list(value: list) -> list:
    if not value:
        raise ValueError("must be a non-empty list")
    return value


class ComponentMetadata(BaseModel):
    """One curated description of an architectural component type."""

    type: NodeType = Field(description="Must match the filename and the NodeType enum value.")
    label: str = Field(description="Human-readable name.")
    description: str = Field(description="1-2 sentence summary.")
    typical_implementations: list[str] = Field(
        description="Concrete examples — 'PostgreSQL', 'MySQL', 'SQLite'."
    )
    common_pairings: list[NodeType] = Field(
        description="Node types this commonly connects to. Validated against the closed enum."
    )
    tradeoffs: list[str] = Field(
        description="Bullet-style 'gain X / pay Y' notes for a junior reader."
    )
    anti_patterns: list[str] = Field(description="Bullet-style 'do not do this because…' notes.")
    learning_resources: list[str] = Field(
        default_factory=list,
        description="Optional links / references.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Free-form taxonomy (e.g. 'stateful', 'managed-saas').",
    )

    # --- Validators for required prose / list fields ------------------------

    @field_validator("label", "description")
    @classmethod
    def _check_non_empty_str(cls, v: str) -> str:
        return _non_empty_str(v)

    @field_validator("typical_implementations", "common_pairings", "tradeoffs", "anti_patterns")
    @classmethod
    def _check_non_empty_list(cls, v: list) -> list:
        return _non_empty_list(v)
