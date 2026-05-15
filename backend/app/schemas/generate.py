"""Schemas for the POST /generate endpoint.

The LLM is asked for `GeneratedDiagramContent` — just the parts the model
should decide. The backend wraps that into a full `Diagram` by adding a
ULID, server timestamps, and positions assigned by auto_layout.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.diagram import DataFlow, NodeType


class GenerateRequest(BaseModel):
    """Request body for POST /generate."""

    prompt: str = Field(
        min_length=1,
        description="Free-text description of what the user wants to design.",
    )

    @field_validator("prompt")
    @classmethod
    def _strip_and_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("prompt must not be empty after stripping whitespace")
        return v


# --- LLM-facing schemas -------------------------------------------------------


class GeneratedNodeAI(BaseModel):
    """Pedagogical commentary the LLM may attach to a node."""

    explanation: str | None = None
    rationale: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class GeneratedNode(BaseModel):
    """A node as the LLM is asked to produce it (no position)."""

    id: str = Field(min_length=1, description="LLM-chosen unique id within this diagram.")
    type: NodeType
    label: str = Field(min_length=1)
    properties: dict[str, Any] = Field(default_factory=dict)
    ai: GeneratedNodeAI | None = None


class GeneratedEdgeProperties(BaseModel):
    protocol: str | None = None
    data_flow: DataFlow | None = Field(default=None, alias="dataFlow")


class GeneratedEdgeAI(BaseModel):
    explanation: str | None = None


class GeneratedEdge(BaseModel):
    """An edge as the LLM is asked to produce it."""

    id: str = Field(min_length=1)
    source: str
    target: str
    label: str | None = None
    properties: GeneratedEdgeProperties = Field(default_factory=GeneratedEdgeProperties)
    ai: GeneratedEdgeAI | None = None


class GeneratedDiagramContent(BaseModel):
    """What the LLM returns — content only. Backend owns id/timestamps/positions."""

    name: str = Field(min_length=1, description="Short title for the diagram.")
    description: str | None = None
    nodes: list[GeneratedNode] = Field(min_length=1)
    edges: list[GeneratedEdge] = Field(default_factory=list)
