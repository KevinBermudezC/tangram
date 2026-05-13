"""Rule: a node with no incident edges is probably forgotten."""

from __future__ import annotations

from app.schemas.diagram import Diagram
from app.schemas.finding import Finding, Severity


class IsolatedNode:
    id = "isolated-node"
    severity = Severity.WARNING
    title = "Node has no connections"
    description = (
        "Nodes with no inbound or outbound edges are typically leftovers from "
        "editing — a piece you dragged out and forgot to wire up. If this is "
        "intentional (a node you're documenting but not modeling yet), feel "
        "free to ignore the warning."
    )

    def check(self, diagram: Diagram) -> list[Finding]:
        referenced: set[str] = set()
        for edge in diagram.edges:
            referenced.add(edge.source)
            referenced.add(edge.target)
        findings: list[Finding] = []
        for node in diagram.nodes:
            if node.id not in referenced:
                findings.append(
                    Finding(
                        rule_id=self.id,
                        severity=self.severity,
                        message=f"{node.label} has no connections.",
                        rationale=self.description,
                        node_ids=[node.id],
                    )
                )
        return findings
