from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    AUTH = "auth"
    STORAGE = "storage"
    EXTERNAL_SERVICE = "external_service"
    QUEUE = "queue"
    CACHE = "cache"


class DataFlow(str, Enum):
    UNIDIRECTIONAL = "unidirectional"
    BIDIRECTIONAL = "bidirectional"


class MessageRole(str, Enum):
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