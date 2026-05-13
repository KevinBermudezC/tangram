"""Rule: a frontend node must not connect directly to a database node."""

from __future__ import annotations

from app.schemas.diagram import Diagram, NodeType
from app.schemas.finding import Finding, Severity


class NoDirectFrontendToDatabase:
    id = "no-direct-frontend-to-database"
    severity = Severity.ERROR
    title = "Frontend connects directly to database"
    description = (
        "Frontend nodes should never connect directly to a database. All data "
        "access should go through a backend that enforces authorization and "
        "input validation. A direct frontend-to-database edge typically means "
        "credentials live in the browser (where they can be exfiltrated) and "
        "access control is unenforceable."
    )

    def check(self, diagram: Diagram) -> list[Finding]:
        nodes_by_id = {n.id: n for n in diagram.nodes}
        findings: list[Finding] = []
        for edge in diagram.edges:
            source = nodes_by_id.get(edge.source)
            target = nodes_by_id.get(edge.target)
            if source is None or target is None:
                continue
            types = {source.type, target.type}
            if types == {NodeType.FRONTEND, NodeType.DATABASE}:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        severity=self.severity,
                        message=f"{source.label} connects directly to {target.label}",
                        rationale=self.description,
                        node_ids=[source.id, target.id],
                        edge_ids=[edge.id],
                    )
                )
        return findings
