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


class DiagramSummary(BaseModel):
    """Lightweight projection of a Diagram for list views (no nodes/edges).

    Backs `GET /diagrams`: the library only needs enough to render a card and
    open the full diagram by id, not every node and edge.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    node_count: int = Field(alias="nodeCount")
    edge_count: int = Field(alias="edgeCount")

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
        )
