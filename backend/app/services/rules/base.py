"""Rule protocol — every built-in rule and any contributor rule conforms to this."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.schemas.diagram import Diagram
from app.schemas.finding import Finding, Severity


@runtime_checkable
class Rule(Protocol):
    """Structural contract for a rule.

    Any class with these four attributes and a `check(diagram)` method is a Rule.
    No base class to inherit from — Python `Protocol` gives us this for free.
    """

    id: str
    severity: Severity
    title: str
    description: str

    def check(self, diagram: Diagram) -> list[Finding]:
        """Inspect the diagram and return findings (empty list if nothing wrong)."""
        ...
