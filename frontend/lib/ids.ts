/**
 * Client-side id minting for canvas-created nodes/edges.
 *
 * Node ids in the Tangram schema are free-form strings — the backend only
 * checks uniqueness within a diagram and that edges reference existing nodes.
 * A short random suffix is plenty to avoid collisions in one diagram, and a
 * type prefix keeps ids readable in serialized JSON.
 */

function shortId(): string {
  // crypto.randomUUID is available in every browser the app targets.
  return crypto.randomUUID().slice(0, 8);
}

export function newNodeId(type: string): string {
  return `${type}-${shortId()}`;
}

export function newEdgeId(): string {
  return `e-${shortId()}`;
}

/** A client-minted diagram id for blank-canvas drafts (Crockford-ish, sortable enough). */
export function newDiagramId(): string {
  return `d-${crypto.randomUUID().replace(/-/g, "").slice(0, 20)}`;
}
