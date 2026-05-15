import type { NodeType } from "@/types/tangram";

/**
 * Per-category fills + strokes used by node cards, palette icons, and the
 * mini thumbnails. Tokens come from `app/globals.css` so the values stay
 * single-sourced; this file just maps node type → token names.
 */
export const nodeColors: Record<
  NodeType,
  { fill: string; ink: string; label: string }
> = {
  frontend: {
    fill: "var(--color-cat-frontend)",
    ink: "var(--color-cat-frontend-ink)",
    label: "Frontend",
  },
  backend: {
    fill: "var(--color-cat-backend)",
    ink: "var(--color-cat-backend-ink)",
    label: "Backend",
  },
  database: {
    fill: "var(--color-cat-database)",
    ink: "var(--color-cat-database-ink)",
    label: "Database",
  },
  auth: {
    fill: "var(--color-cat-auth)",
    ink: "var(--color-cat-auth-ink)",
    label: "Auth",
  },
  storage: {
    fill: "var(--color-cat-storage)",
    ink: "var(--color-cat-storage-ink)",
    label: "Storage",
  },
  external_service: {
    fill: "var(--color-cat-external)",
    ink: "var(--color-cat-external-ink)",
    label: "External API",
  },
  queue: {
    fill: "var(--color-cat-queue)",
    ink: "var(--color-cat-queue-ink)",
    label: "Queue",
  },
  cache: {
    fill: "var(--color-cat-cache)",
    ink: "var(--color-cat-cache-ink)",
    label: "Cache",
  },
};

/** Lucide icon name per node type (kept here so the palette + cards share). */
export const nodeIconName: Record<NodeType, string> = {
  frontend: "Monitor",
  backend: "Server",
  database: "Database",
  auth: "ShieldCheck",
  storage: "HardDrive",
  external_service: "Globe",
  queue: "Layers",
  cache: "Zap",
};
