from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NodeType(StrEnum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    AUTH = "auth"
    STORAGE = "storage"
    EXTERNAL_SERVICE = "external_service"
    QUEUE = "queue"
    CACHE = "cache"


class DataFlow(StrEnum):
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Position(BaseModel):
    x: float
    y: float


class NodeAI(BaseModel):
    explanation: str | None = None
    rationale: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class Node(BaseModel):
    id: str
    type: NodeType
    label: str
    position: Position
    properties: dict[str, Any] = Field(default_factory=dict)
    ai: NodeAI | None = None


class EdgeProperties(BaseModel):
    protocol: str | None = None
    data_flow: DataFlow | None = Field(default=None, alias="dataFlow")


class EdgeAI(BaseModel):
    explanation: str | None = None


class Edge(BaseModel):
    id: str
    source: str
    target: str
    label: str | None = None
    properties: EdgeProperties = Field(default_factory=EdgeProperties)
    ai: EdgeAI | None = None


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime


class DiagramMetadata(BaseModel):
    name: str
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class Diagram(BaseModel):
    """Canonical schema for a Tangram diagram. See docs/schema/diagram-v0.md."""

    version: str = "0.1.0"
    id: str
    metadata: DiagramMetadata
    nodes: list[Node]
    edges: list[Edge]
    conversation: list[Message] = Field(default_factory=list)


# --- Thumbnail projection ----------------------------------------------------
# A downscaled, label-free sketch of a diagram for library cards. Node
# positions are normalized into a fixed 200x120 viewBox so the frontend can
# render an SVG preview without fetching every full node/edge.

_THUMB_W = 200.0
_THUMB_H = 120.0
_THUMB_NODE_W = 30.0
_THUMB_NODE_H = 22.0
_THUMB_PAD = 14.0


class ThumbPoint(BaseModel):
    x: float
    y: float


class ThumbNode(BaseModel):
    """A node rect in thumbnail coordinates (top-left origin)."""

    type: NodeType
    x: float
    y: float
    w: float = _THUMB_NODE_W
    h: float = _THUMB_NODE_H


class ThumbEdge(BaseModel):
    """An edge in thumbnail coordinates, endpoints at node-rect centers."""

    model_config = ConfigDict(populate_by_name=True)

    from_: ThumbPoint = Field(alias="from")
    to: ThumbPoint
    dashed: bool = False


class DiagramThumb(BaseModel):
    """Geometry-only preview: node rects + edge lines, no labels or props."""

    nodes: list[ThumbNode]
    edges: list[ThumbEdge]


def _scale(value: float, lo: float, hi: float, out_lo: float, out_hi: float) -> float:
    """Map ``value`` from ``[lo, hi]`` into ``[out_lo, out_hi]``.

    When the source range is degenerate (single node, or a column with no
    spread) the output is centered rather than dividing by zero.
    """
    if hi - lo < 1e-9:
        return (out_lo + out_hi) / 2
    return out_lo + (value - lo) / (hi - lo) * (out_hi - out_lo)


def build_thumb(diagram: Diagram) -> DiagramThumb:
    """Project a diagram's node positions into a 200x120 thumbnail."""
    if not diagram.nodes:
        return DiagramThumb(nodes=[], edges=[])

    xs = [n.position.x for n in diagram.nodes]
    ys = [n.position.y for n in diagram.nodes]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Center range keeps whole rects inside the padded viewBox.
    cx_lo, cx_hi = _THUMB_PAD + _THUMB_NODE_W / 2, _THUMB_W - _THUMB_PAD - _THUMB_NODE_W / 2
    cy_lo, cy_hi = _THUMB_PAD + _THUMB_NODE_H / 2, _THUMB_H - _THUMB_PAD - _THUMB_NODE_H / 2

    centers: dict[str, ThumbPoint] = {}
    thumb_nodes: list[ThumbNode] = []
    for node in diagram.nodes:
        cx = _scale(node.position.x, min_x, max_x, cx_lo, cx_hi)
        cy = _scale(node.position.y, min_y, max_y, cy_lo, cy_hi)
        centers[node.id] = ThumbPoint(x=cx, y=cy)
        thumb_nodes.append(
            ThumbNode(type=node.type, x=cx - _THUMB_NODE_W / 2, y=cy - _THUMB_NODE_H / 2)
        )

    thumb_edges: list[ThumbEdge] = []
    for edge in diagram.edges:
        src = centers.get(edge.source)
        dst = centers.get(edge.target)
        if src is None or dst is None:
            continue  # dangling edge — skip rather than draw a line to nowhere
        # Dashed = the model annotated this edge (mirrors the prototype's
        # "AI-drawn = dashed" convention).
        thumb_edges.append(ThumbEdge(from_=src, to=dst, dashed=edge.ai is not None))

    return DiagramThumb(nodes=thumb_nodes, edges=thumb_edges)


class DiagramSummary(BaseModel):
    """Lightweight projection of a Diagram for list views (no full nodes/edges).

    Backs `GET /diagrams`: the library needs enough to render a card (name,
    counts, a geometry-only `thumb`) and open the full diagram by id — not
    every node label, property, and AI annotation.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    node_count: int = Field(alias="nodeCount")
    edge_count: int = Field(alias="edgeCount")
    thumb: DiagramThumb

    @classmethod
    def from_diagram(cls, diagram: Diagram) -> "DiagramSummary":
        return cls(
            id=diagram.id,
            name=diagram.metadata.name,
            description=diagram.metadata.description,
            created_at=diagram.metadata.created_at,
            updated_at=diagram.metadata.updated_at,
            node_count=len(diagram.nodes),
            edge_count=len(diagram.edges),
            thumb=build_thumb(diagram),
        )
