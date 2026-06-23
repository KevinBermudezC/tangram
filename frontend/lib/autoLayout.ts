import Dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@xyflow/react";

const DEFAULT_NODE_W = 200;
const DEFAULT_NODE_H = 48;

/**
 * Tidy a graph into a clean left-to-right layered layout (Dagre). Returns the
 * nodes with new positions; edges are unchanged. Node sizes use React Flow's
 * measured dimensions when available so spacing accounts for real widths.
 */
export function autoLayout(nodes: Node[], edges: Edge[]): Node[] {
  if (nodes.length === 0) return nodes;

  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "LR", nodesep: 70, ranksep: 140, marginx: 40, marginy: 40 });

  for (const node of nodes) {
    g.setNode(node.id, {
      width: node.measured?.width ?? DEFAULT_NODE_W,
      height: node.measured?.height ?? DEFAULT_NODE_H,
    });
  }
  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  Dagre.layout(g);

  return nodes.map((node) => {
    const pos = g.node(node.id);
    const w = node.measured?.width ?? DEFAULT_NODE_W;
    const h = node.measured?.height ?? DEFAULT_NODE_H;
    // Dagre returns node centres; React Flow positions are top-left.
    return {
      ...node,
      position: { x: pos.x - w / 2, y: pos.y - h / 2 },
    };
  });
}
