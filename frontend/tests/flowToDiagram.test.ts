import type { Edge as RFEdge, Node as RFNode } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { diagramToFlow } from "@/lib/diagramToFlow";
import { flowToDiagram } from "@/lib/flowToDiagram";
import type { Diagram } from "@/types/tangram";

function makeDiagram(): Diagram {
  return {
    version: "0.1.0",
    id: "test-diagram",
    metadata: {
      name: "Delivery app",
      description: null,
      createdAt: "2026-05-09T00:00:00Z",
      updatedAt: "2026-05-09T00:00:00Z",
    },
    nodes: [
      { id: "front", type: "frontend", label: "App", position: { x: 80, y: 240 }, properties: {} },
      { id: "api", type: "backend", label: "API", position: { x: 560, y: 240 }, properties: {} },
      { id: "db", type: "database", label: "DB", position: { x: 800, y: 240 }, properties: {} },
    ],
    edges: [
      { id: "e1", source: "front", target: "api", properties: {} },
      { id: "e2", source: "api", target: "db", properties: {} },
    ],
    conversation: [],
  };
}

describe("flowToDiagram", () => {
  it("round-trips a diagram through diagramToFlow without losing the graph", () => {
    const original = makeDiagram();
    const { nodes, edges } = diagramToFlow(original);
    const result = flowToDiagram(nodes, edges, original);

    expect(result.nodes.map((n) => n.id)).toEqual(["front", "api", "db"]);
    expect(result.nodes.map((n) => n.type)).toEqual(["frontend", "backend", "database"]);
    expect(result.nodes.map((n) => n.position)).toEqual([
      { x: 80, y: 240 },
      { x: 560, y: 240 },
      { x: 800, y: 240 },
    ]);
    expect(result.edges.map((e) => [e.source, e.target])).toEqual([
      ["front", "api"],
      ["api", "db"],
    ]);
  });

  it("carries through version, id, metadata, and conversation from base", () => {
    const original = makeDiagram();
    const { nodes, edges } = diagramToFlow(original);
    const result = flowToDiagram(nodes, edges, original);
    expect(result.id).toBe("test-diagram");
    expect(result.version).toBe("0.1.0");
    expect(result.metadata.name).toBe("Delivery app");
  });

  it("serializes a canvas-created node (no stashed tangram payload)", () => {
    const base = makeDiagram();
    const nodes: RFNode[] = [
      {
        id: "cache-abc123",
        position: { x: 12.6, y: 40.2 },
        data: { label: "Cache", tangramType: "cache" },
        type: "tangram",
      },
    ];
    const result = flowToDiagram(nodes, [], base);
    expect(result.nodes[0]).toMatchObject({
      id: "cache-abc123",
      type: "cache",
      label: "Cache",
      position: { x: 13, y: 40 },
      properties: {},
    });
  });

  it("drops edges referencing missing nodes", () => {
    const base = makeDiagram();
    const nodes: RFNode[] = [
      { id: "a", position: { x: 0, y: 0 }, data: { label: "A", tangramType: "frontend" }, type: "tangram" },
    ];
    const edges: RFEdge[] = [
      { id: "bad", source: "a", target: "ghost" },
      { id: "alsoBad", source: "ghost", target: "a" },
    ];
    const result = flowToDiagram(nodes, edges, base);
    expect(result.edges).toEqual([]);
  });
});
