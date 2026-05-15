// -----------------------------------------------------------------------------
// HAND-WRITTEN. This file mirrors backend/app/schemas/diagram.py and related
// Pydantic schemas. It will be replaced by auto-generated types when the
// `add-openapi-typescript-codegen` proposal lands. Until then, any change
// to the backend schema must be reflected here in the same PR.
// -----------------------------------------------------------------------------

export type NodeType =
  | "frontend"
  | "backend"
  | "database"
  | "auth"
  | "storage"
  | "external_service"
  | "queue"
  | "cache";

export type DataFlow = "unidirectional" | "bidirectional";

export type MessageRole = "user" | "assistant";

export interface Position {
  x: number;
  y: number;
}

export interface NodeAI {
  explanation?: string | null;
  rationale?: string | null;
  confidence?: number | null;
}

export interface DiagramNode {
  id: string;
  type: NodeType;
  label: string;
  position: Position;
  properties: Record<string, unknown>;
  ai?: NodeAI | null;
}

export interface EdgeProperties {
  protocol?: string | null;
  dataFlow?: DataFlow | null;
}

export interface EdgeAI {
  explanation?: string | null;
}

export interface DiagramEdge {
  id: string;
  source: string;
  target: string;
  label?: string | null;
  properties: EdgeProperties;
  ai?: EdgeAI | null;
}

export interface ConversationMessage {
  role: MessageRole;
  content: string;
  timestamp: string; // ISO 8601
}

export interface DiagramMetadata {
  name: string;
  description?: string | null;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
}

export interface Diagram {
  version: string;
  id: string;
  metadata: DiagramMetadata;
  nodes: DiagramNode[];
  edges: DiagramEdge[];
  conversation: ConversationMessage[];
}

// --- API error contract ------------------------------------------------------

export interface ApiErrorBody {
  detail: string;
  code: string;
}
