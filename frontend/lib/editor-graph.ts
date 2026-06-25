import type { Connection, Edge, Node, XYPosition } from "@xyflow/react";
import { addEdge } from "@xyflow/react";

import { newEdgeId, newNodeId } from "@/lib/ids";
import { nodeColors } from "@/lib/node-style";
import type { NodeType } from "@/types/tangram";

/**
 * Pure graph mutations used by the interactive canvas. Kept out of the React
 * component so they can be unit-tested without rendering React Flow (which
 * needs real DOM measurements).
 */

/**
 * Apply a new connection: reject self-loops and duplicate (source,target)
 * pairs, otherwise append an edge with a fresh id. Returns the same array
 * reference when the connection is rejected (no-op).
 */
export function connectEdge(edges: Edge[], connection: Connection): Edge[] {
  if (!connection.source || !connection.target) return edges;
  if (connection.source === connection.target) return edges;
  const duplicate = edges.some(
    (e) => e.source === connection.source && e.target === connection.target,
  );
  if (duplicate) return edges;
  return addEdge({ ...connection, id: newEdgeId() }, edges);
}

/** Build a new canvas node of `type` at `position` with a default label. */
export function createNode(type: NodeType, position: XYPosition): Node {
  return {
    id: newNodeId(type),
    type: "tangram",
    position,
    data: {
      label: nodeColors[type]?.label ?? type,
      tangramType: type,
    },
  };
}
