"""Lightweight diagram factories for rule tests.

Each test only cares about a tiny subset of the schema. These helpers build a
minimum-viable `Diagram` so each test can focus on the rule under test.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.diagram import (
    DataFlow,
    Diagram,
    DiagramMetadata,
    Edge,
    EdgeProperties,
    Node,
    NodeType,
    Position,
)


def _now() -> datetime:
    return datetime.now(UTC)


def make_node(node_id: str, node_type: NodeType, label: str | None = None) -> Node:
    return Node(
        id=node_id,
        type=node_type,
        label=label or f"{node_type.value}-{node_id}",
        position=Position(x=0, y=0),
    )


def make_edge(
    edge_id: str,
    source: str,
    target: str,
    data_flow: DataFlow = DataFlow.UNIDIRECTIONAL,
) -> Edge:
    return Edge(
        id=edge_id,
        source=source,
        target=target,
        properties=EdgeProperties(data_flow=data_flow),
    )


def make_diagram(nodes: list[Node], edges: list[Edge], name: str = "test") -> Diagram:
    now = _now()
    # The DiagramMetadata schema uses camelCase aliases on the wire and does
    # not currently set populate_by_name, so we construct via model_validate.
    metadata = DiagramMetadata.model_validate({"name": name, "createdAt": now, "updatedAt": now})
    return Diagram(
        id=f"diag-{name}",
        metadata=metadata,
        nodes=nodes,
        edges=edges,
    )
