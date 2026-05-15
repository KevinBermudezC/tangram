/**
 * Static mock data for the prototype port.
 *
 * Once persistence endpoints land (`add-diagram-persistence-routes` proposal),
 * these go away and the home/library pages call the backend instead.
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

export const recentDiagrams: MockDiagram[] = [
  {
    id: "01KRP1RSEQHMVTVNTY2FY3NXBQ",
    name: "Delivery App",
    source: "ai",
    components: 5,
    connections: 5,
    updatedLabel: "12s ago",
    thumb: {
      nodes: [
        { type: "frontend", x: 10, y: 46, w: 28, h: 28 },
        { type: "backend", x: 70, y: 46, w: 34, h: 28 },
        { type: "auth", x: 70, y: 6, w: 34, h: 22 },
        { type: "database", x: 150, y: 46, w: 34, h: 28 },
        { type: "storage", x: 150, y: 84, w: 34, h: 22 },
      ],
      edges: [
        { from: { x: 38, y: 60 }, to: { x: 70, y: 60 }, dashed: true },
        { from: { x: 87, y: 46 }, to: { x: 87, y: 28 }, dashed: true },
        { from: { x: 104, y: 60 }, to: { x: 150, y: 60 }, dashed: true },
      ],
    },
  },
  {
    id: "01KRP1XYZ-saas",
    name: "SaaS dashboard",
    source: "manual",
    components: 5,
    connections: 4,
    updatedLabel: "2h ago",
    thumb: {
      nodes: [
        { type: "frontend", x: 12, y: 16, w: 28, h: 28 },
        { type: "cache", x: 12, y: 76, w: 28, h: 28 },
        { type: "backend", x: 80, y: 16, w: 36, h: 28 },
        { type: "queue", x: 80, y: 76, w: 36, h: 28 },
        { type: "database", x: 156, y: 46, w: 32, h: 28 },
      ],
      edges: [
        { from: { x: 40, y: 30 }, to: { x: 80, y: 30 } },
        { from: { x: 40, y: 90 }, to: { x: 80, y: 90 } },
        { from: { x: 115, y: 30 }, to: { x: 115, y: 90 } },
      ],
    },
  },
  {
    id: "01KRP1XYZ-twitter",
    name: "Twitter clone with notifications",
    source: "ai",
    components: 6,
    connections: 7,
    updatedLabel: "yesterday",
    thumb: {
      nodes: [
        { type: "frontend", x: 12, y: 46, w: 28, h: 28 },
        { type: "queue", x: 83, y: 0, w: 30, h: 22 },
        { type: "backend", x: 83, y: 46, w: 30, h: 28 },
        { type: "cache", x: 83, y: 98, w: 30, h: 22 },
        { type: "database", x: 153, y: 46, w: 34, h: 28 },
      ],
      edges: [
        { from: { x: 40, y: 60 }, to: { x: 83, y: 60 }, dashed: true },
        { from: { x: 113, y: 60 }, to: { x: 153, y: 60 }, dashed: true },
        { from: { x: 97, y: 46 }, to: { x: 97, y: 22 }, dashed: true },
        { from: { x: 97, y: 74 }, to: { x: 97, y: 98 }, dashed: true },
      ],
    },
  },
  {
    id: "01KRP1XYZ-untitled",
    name: "Untitled diagram",
    source: "draft",
    components: 1,
    connections: 0,
    updatedLabel: "not saved",
    thumb: {
      nodes: [{ type: "frontend", x: 58, y: 42, w: 36, h: 28 }],
      edges: [],
    },
  },
  {
    id: "01KRP1XYZ-auth",
    name: "Internal auth playground",
    source: "manual",
    components: 4,
    connections: 3,
    updatedLabel: "3 days ago",
    thumb: {
      nodes: [
        { type: "frontend", x: 14, y: 46, w: 30, h: 28 },
        { type: "auth", x: 100, y: 0, w: 40, h: 22 },
        { type: "backend", x: 100, y: 46, w: 40, h: 28 },
        { type: "database", x: 100, y: 98, w: 40, h: 22 },
      ],
      edges: [
        { from: { x: 44, y: 60 }, to: { x: 100, y: 60 } },
        { from: { x: 120, y: 46 }, to: { x: 120, y: 22 } },
        { from: { x: 120, y: 74 }, to: { x: 120, y: 98 } },
      ],
    },
  },
  {
    id: "01KRP1XYZ-crm",
    name: "Multi-tenant CRM",
    source: "ai",
    components: 5,
    connections: 4,
    updatedLabel: "last week",
    thumb: {
      nodes: [
        { type: "frontend", x: 12, y: 20, w: 28, h: 32 },
        { type: "frontend", x: 12, y: 68, w: 28, h: 32 },
        { type: "backend", x: 80, y: 20, w: 30, h: 32 },
        { type: "queue", x: 80, y: 68, w: 30, h: 32 },
        { type: "database", x: 152, y: 20, w: 34, h: 32 },
      ],
      edges: [
        { from: { x: 40, y: 36 }, to: { x: 80, y: 36 }, dashed: true },
        { from: { x: 40, y: 84 }, to: { x: 80, y: 84 }, dashed: true },
        { from: { x: 110, y: 36 }, to: { x: 152, y: 36 }, dashed: true },
      ],
    },
  },
];

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
