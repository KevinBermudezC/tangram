"""Schemas for the POST /analyze endpoint.

`/analyze` is the inverse of `/generate`: it takes an existing `Diagram` and
returns the deterministic rule findings plus an LLM-generated prose critique.
The findings come straight from the rules engine; the feedback is the tutor's
narrative around them.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.diagram import Diagram
from app.schemas.finding import Finding


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    model_config = ConfigDict(populate_by_name=True)

    diagram: Diagram = Field(description="The diagram to analyze. Never mutated or persisted.")
    mode_id: str = Field(
        default="tutor",
        alias="modeId",
        description="Which mode persona drives the prose feedback. Defaults to tutor.",
    )


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""

    findings: list[Finding] = Field(
        description="Deterministic rule-engine output for the submitted diagram.",
    )
    feedback: str = Field(
        description="Human-readable critique from the LLM, grounded in the findings.",
    )
