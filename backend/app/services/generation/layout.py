"""Deterministic column-by-type auto-layout for generated diagrams.

The LLM produces nodes without positions. We assign positions here based on
node type. The result is a readable left-to-right data flow:

    frontend  →  auth  →  backend  →  database
                                   →  storage
              external_service (top row)
              cache / queue (around backend)
"""

from __future__ import annotations

from app.schemas.diagram import Node, NodeType, Position
from app.schemas.generate import GeneratedNode

# Layout constants — tuned for ~6–10 node diagrams, readable in React Flow.
_COLUMN_X: dict[NodeType, float] = {
    NodeType.FRONTEND: 80,
    NodeType.AUTH: 320,
    NodeType.BACKEND: 560,
    NodeType.CACHE: 560,
    NodeType.QUEUE: 560,
    NodeType.DATABASE: 800,
    NodeType.STORAGE: 800,
    NodeType.EXTERNAL_SERVICE: 320,  # top row, see y offset below
}

_DEFAULT_Y = 240
_ROW_GAP = 160

# Types that get a different "row" treatment (e.g. external services go up top,
# cache/queue go below backend).
_TOP_ROW_TYPES = {NodeType.EXTERNAL_SERVICE}
_BOTTOM_ROW_TYPES = {NodeType.CACHE, NodeType.QUEUE}


def _base_y_for(node_type: NodeType) -> float:
    if node_type in _TOP_ROW_TYPES:
        return 80
    if node_type in _BOTTOM_ROW_TYPES:
        return _DEFAULT_Y + _ROW_GAP
    return _DEFAULT_Y


def auto_layout(generated_nodes: list[GeneratedNode]) -> list[Node]:
    """Convert a list of position-less LLM-produced nodes into positioned ones.

    Stable across runs: same input order → same output positions.
    """
    # Track how many of each type we've placed so we can stack vertically.
    type_counts: dict[NodeType, int] = {}
    out: list[Node] = []
    for gen in generated_nodes:
        seen = type_counts.get(gen.type, 0)
        type_counts[gen.type] = seen + 1

        x = _COLUMN_X.get(gen.type, 560)
        base_y = _base_y_for(gen.type)
        # Stack additional nodes of the same type below the first one.
        y = base_y + seen * _ROW_GAP

        out.append(
            Node(
                id=gen.id,
                type=gen.type,
                label=gen.label,
                position=Position(x=x, y=y),
                properties=dict(gen.properties),
                ai=_translate_ai(gen.ai),
            )
        )
    return out


def _translate_ai(ai):  # noqa: ANN001
    """Translate the LLM-facing GeneratedNodeAI to the canonical NodeAI shape."""
    if ai is None:
        return None
    from app.schemas.diagram import NodeAI

    return NodeAI(
        explanation=ai.explanation,
        rationale=ai.rationale,
        confidence=ai.confidence,
    )
