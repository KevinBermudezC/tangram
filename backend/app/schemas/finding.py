"""Finding shape — what a rule emits when it detects something.

Findings are returned by rules in the anti-pattern engine and will eventually
flow back to the frontend (to highlight offending nodes/edges) and to the LLM
(as context for the explanation pass in /analyze).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Finding(BaseModel):
    """A single rule violation."""

    rule_id: str = Field(description="The id of the rule that produced this finding.")
    severity: Severity
    message: str = Field(description="Short, user-facing summary.")
    rationale: str = Field(description="The pedagogical why — pulled from the rule's description.")
    node_ids: list[str] = Field(
        default_factory=list,
        description="Node ids involved in the violation.",
    )
    edge_ids: list[str] = Field(
        default_factory=list,
        description="Edge ids directly responsible for the violation.",
    )
