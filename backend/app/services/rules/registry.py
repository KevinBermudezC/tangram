"""Registry of built-in rules.

Adding a rule = import it here and append an instance to `_BUILT_IN_RULES`.
We deliberately keep this explicit (no filesystem walking) so the ordering
is stable and refactors don't surprise anyone.
"""

from __future__ import annotations

from app.schemas.diagram import Diagram
from app.schemas.finding import Finding
from app.services.rules.base import Rule
from app.services.rules.rules.cycle_detected import CycleDetected
from app.services.rules.rules.frontend_with_db_needs_auth import FrontendWithDbNeedsAuth
from app.services.rules.rules.isolated_node import IsolatedNode
from app.services.rules.rules.no_direct_frontend_to_database import (
    NoDirectFrontendToDatabase,
)
from app.services.rules.rules.no_direct_frontend_to_storage import (
    NoDirectFrontendToStorage,
)

_BUILT_IN_RULES: list[Rule] = [
    NoDirectFrontendToDatabase(),
    NoDirectFrontendToStorage(),
    FrontendWithDbNeedsAuth(),
    IsolatedNode(),
    CycleDetected(),
]


def all_rules() -> list[Rule]:
    """Return every built-in rule, in registration order."""
    return list(_BUILT_IN_RULES)


def check_all(diagram: Diagram) -> list[Finding]:
    """Run every built-in rule and return the union of their findings."""
    findings: list[Finding] = []
    for rule in _BUILT_IN_RULES:
        findings.extend(rule.check(diagram))
    return findings
