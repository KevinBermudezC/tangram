import type { Edge as RFEdge, Node as RFNode } from "@xyflow/react";

import type {
  Diagram,
  DiagramEdge,
  DiagramNode,
  EdgeProperties,
  NodeType,
} from "@/types/tangram";

/**
 * Reverse of `diagramToFlow`: serialize the live React Flow graph back into a
 * Tangram `Diagram`.
 *
 * `base` supplies the fields the canvas doesn't represent — version, id,
 * metadata, conversation — which are carried through unchanged. Node/edge
 * payloads stashed in `data.tangram` (properties, ai) are preserved so a
 * round-trip is lossless; canvas-created elements fall back to sensible empties.
 *
 * Edges referencing a node id that no longer exists are dropped, so the result
 * always satisfies the backend's edge-integrity check.
 */
export function flowToDiagram(
  nodes: RFNode[],
  edges: RFEdge[],
  base: Diagram,
): Diagram {
  const tangramNodes = nodes.map(toTangramNode);
  const nodeIds = new Set(tangramNodes.map((n) => n.id));
  const tangramEdges = edges
    .filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target))
    .map(toTangramEdge);

  return {
    ...base,
    nodes: tangramNodes,
    edges: tangramEdges,
  };
}

function toTangramNode(node: RFNode): DiagramNode {
  const data = (node.data ?? {}) as Record<string, unknown>;
  const prev = (data.tangram ?? {}) as Partial<DiagramNode>;
  return {
    id: node.id,
    type: (data.tangramType ?? prev.type) as NodeType,
    label: (data.label as string | undefined) ?? prev.label ?? "",
    position: {
      x: Math.round(node.position.x),
      y: Math.round(node.position.y),
    },
    properties: prev.properties ?? {},
    ai: prev.ai ?? null,
  };
}

function toTangramEdge(edge: RFEdge): DiagramEdge {
  const data = (edge.data ?? {}) as Record<string, unknown>;
  const prev = (data.tangram ?? {}) as Partial<DiagramEdge>;
  const label =
    typeof edge.label === "string" ? edge.label : (prev.label ?? null);
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label,
    properties: (prev.properties ?? {}) as EdgeProperties,
    ai: prev.ai ?? null,
  };
}
