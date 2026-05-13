"""Rule: a frontend node must not connect directly to a storage node."""

from __future__ import annotations

from app.schemas.diagram import Diagram, NodeType
from app.schemas.finding import Finding, Severity


class NoDirectFrontendToStorage:
    id = "no-direct-frontend-to-storage"
    severity = Severity.ERROR
    title = "Frontend connects directly to storage"
    description = (
        "Frontend nodes should not connect directly to object/file storage. "
        "Even with pre-signed URLs (a legitimate way to do direct browser "
        "uploads), the handshake is mediated by the backend that issues the "
        "URL — it is not modeled as a frontend-to-storage edge. A direct edge "
        "typically means public-bucket exposure or hardcoded credentials in "
        "the browser."
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
            if types == {NodeType.FRONTEND, NodeType.STORAGE}:
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
