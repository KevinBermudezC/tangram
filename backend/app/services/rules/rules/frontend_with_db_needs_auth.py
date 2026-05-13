"""Rule: if a diagram has a frontend and a database, it should have an auth node."""

from __future__ import annotations

from app.schemas.diagram import Diagram, NodeType
from app.schemas.finding import Finding, Severity


class FrontendWithDbNeedsAuth:
    id = "frontend-with-db-needs-auth"
    severity = Severity.WARNING
    title = "User-facing system has no auth"
    description = (
        "A diagram with a frontend and a database almost always needs an auth "
        "component — even if it's outsourced to a managed provider. Without "
        "auth, every user touches every row. This warning fires when the "
        "diagram has frontend and database nodes but no auth node at all."
    )

    def check(self, diagram: Diagram) -> list[Finding]:
        frontends = [n for n in diagram.nodes if n.type == NodeType.FRONTEND]
        databases = [n for n in diagram.nodes if n.type == NodeType.DATABASE]
        auths = [n for n in diagram.nodes if n.type == NodeType.AUTH]
        if not frontends or not databases:
            return []
        if auths:
            return []
        node_ids = [n.id for n in frontends + databases]
        return [
            Finding(
                rule_id=self.id,
                severity=self.severity,
                message=(
                    f"Diagram has {len(frontends)} frontend(s) and "
                    f"{len(databases)} database(s) but no auth component."
                ),
                rationale=self.description,
                node_ids=node_ids,
            )
        ]
