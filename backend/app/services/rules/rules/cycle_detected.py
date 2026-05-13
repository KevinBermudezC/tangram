"""Rule: directed cycles in the diagram are usually a sign of a coupling problem."""

from __future__ import annotations

from app.schemas.diagram import Diagram
from app.schemas.finding import Finding, Severity


class CycleDetected:
    id = "cycle-detected"
    severity = Severity.WARNING
    title = "Cycle detected"
    description = (
        "Directed cycles in an architecture are usually a sign of tight "
        "coupling or a missing layer of indirection (a queue, an event bus). "
        "Legitimate cycles exist (e.g. a service that retries through itself), "
        "but they're rare enough to flag. Self-loops are always cycles."
    )

    def check(self, diagram: Diagram) -> list[Finding]:
        # Adjacency list of node id -> list of successor node ids.
        adj: dict[str, list[str]] = {n.id: [] for n in diagram.nodes}
        for edge in diagram.edges:
            if edge.source in adj:
                adj[edge.source].append(edge.target)

        # Iterative DFS with coloring: 0 = unvisited, 1 = on stack, 2 = done.
        color: dict[str, int] = dict.fromkeys(adj, 0)
        cycles: list[list[str]] = []

        def dfs(start: str) -> None:
            stack: list[tuple[str, int]] = [(start, 0)]
            path: list[str] = []
            while stack:
                node, idx = stack[-1]
                if idx == 0:
                    if color[node] == 1:
                        # We were already on this node — cycle found.
                        cycle_start = path.index(node)
                        cycles.append(path[cycle_start:] + [node])
                        stack.pop()
                        continue
                    if color[node] == 2:
                        stack.pop()
                        continue
                    color[node] = 1
                    path.append(node)

                neighbors = adj.get(node, [])
                if idx < len(neighbors):
                    stack[-1] = (node, idx + 1)
                    stack.append((neighbors[idx], 0))
                else:
                    color[node] = 2
                    if path and path[-1] == node:
                        path.pop()
                    stack.pop()

        for node_id in adj:
            if color[node_id] == 0:
                dfs(node_id)

        # Dedupe cycles by their set of nodes (rotation-invariant).
        seen: set[frozenset[str]] = set()
        unique_cycles: list[list[str]] = []
        for cycle in cycles:
            key = frozenset(cycle)
            if key in seen:
                continue
            seen.add(key)
            unique_cycles.append(cycle)

        findings: list[Finding] = []
        for cycle in unique_cycles:
            # cycle ends with the start node repeated; drop the duplicate.
            unique_nodes = list(dict.fromkeys(cycle))
            findings.append(
                Finding(
                    rule_id=self.id,
                    severity=self.severity,
                    message=f"Cycle through {len(unique_nodes)} node(s).",
                    rationale=self.description,
                    node_ids=unique_nodes,
                )
            )
        return findings
