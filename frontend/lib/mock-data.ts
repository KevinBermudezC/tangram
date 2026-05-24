/**
 * View models + static catalog data for the UI.
 *
 * `MockDiagram` is the shape the library cards and rail consume; it's now
 * populated from the backend via `useDiagrams` (see lib/hooks.ts), not from a
 * hardcoded list. `componentCatalog` and `templates` below are still static
 * (the palette and templates page have no backend yet).
 */

import type { NodeType } from "@/types/tangram";

export type DiagramSource = "ai" | "manual" | "draft";

export interface DiagramThumbNode {
  type: NodeType;
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DiagramThumbEdge {
  from: { x: number; y: number };
  to: { x: number; y: number };
  /** Whether the model drew it (AI = dashed) or the user (manual = solid). */
  dashed?: boolean;
}

export interface MockDiagram {
  id: string;
  name: string;
  source: DiagramSource;
  components: number;
  connections: number;
  updatedLabel: string;
  thumb: {
    nodes: DiagramThumbNode[];
    edges: DiagramThumbEdge[];
  };
}

// --- The eight component types we expose in the palette --------------------

export interface ComponentMeta {
  type: NodeType;
  name: string;
  hint: string;
}

export const componentCatalog: ComponentMeta[] = [
  { type: "frontend", name: "Frontend", hint: "Web, mobile, CLI" },
  { type: "backend", name: "Backend", hint: "APIs, services" },
  { type: "database", name: "Database", hint: "SQL or document" },
  { type: "auth", name: "Auth", hint: "Identity, OAuth, JWT" },
  { type: "storage", name: "Storage", hint: "Files, blobs, S3" },
  { type: "external_service", name: "External API", hint: "Third-party services" },
  { type: "queue", name: "Queue", hint: "Jobs, events, retry" },
  { type: "cache", name: "Cache", hint: "Redis, in-memory" },
];

// --- Templates -------------------------------------------------------------

export interface TemplateMeta {
  id: string;
  name: string;
  hint: string;
  primaryType: NodeType;
}

export const templates: TemplateMeta[] = [
  {
    id: "tpl-three-tier",
    name: "Three-tier web app",
    hint: "Frontend → Backend → DB. The classic.",
    primaryType: "backend",
  },
  {
    id: "tpl-background-jobs",
    name: "Background jobs",
    hint: "Producer → queue → workers.",
    primaryType: "queue",
  },
  {
    id: "tpl-read-heavy-cache",
    name: "Read-heavy with cache",
    hint: "Backend ↔ Redis ↔ DB.",
    primaryType: "cache",
  },
  {
    id: "tpl-oauth-flow",
    name: "OAuth flow",
    hint: "Frontend → Auth → Backend.",
    primaryType: "auth",
  },
];
