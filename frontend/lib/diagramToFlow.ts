import type { Edge as RFEdge, Node as RFNode } from "@xyflow/react";

import type { Diagram, DiagramEdge, DiagramNode } from "@/types/tangram";

/**
 * Convert a Tangram `Diagram` into the React Flow `{ nodes, edges }` shape.
 *
 * Position from the backend is preserved as-is. The node's `label` becomes
 * React Flow's `data.label`. The original Tangram node/edge is stashed in
 * `data.tangram` for future use (per-node explanations panel, etc.).
 */
export function diagramToFlow(diagram: Diagram): {
  nodes: RFNode[];
  edges: RFEdge[];
} {
  return {
    nodes: diagram.nodes.map(toFlowNode),
    edges: diagram.edges.map(toFlowEdge),
  };
}

function toFlowNode(node: DiagramNode): RFNode {
  return {
    id: node.id,
    position: { x: node.position.x, y: node.position.y },
    data: {
      label: node.label,
      tangramType: node.type,
      tangram: node,
    },
    type: "default",
  };
}

function toFlowEdge(edge: DiagramEdge): RFEdge {
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label ?? undefined,
    data: {
      tangram: edge,
    },
  };
}
