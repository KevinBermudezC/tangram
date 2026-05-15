import { describe, expect, it } from "vitest";

import { diagramToFlow } from "@/lib/diagramToFlow";
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
      {
        id: "front",
        type: "frontend",
        label: "App",
        position: { x: 80, y: 240 },
        properties: {},
      },
      {
        id: "api",
        type: "backend",
        label: "API",
        position: { x: 560, y: 240 },
        properties: {},
      },
      {
        id: "db",
        type: "database",
        label: "DB",
        position: { x: 800, y: 240 },
        properties: {},
      },
    ],
    edges: [
      { id: "e1", source: "front", target: "api", properties: {} },
      { id: "e2", source: "api", target: "db", properties: {} },
    ],
    conversation: [],
  };
}

describe("diagramToFlow", () => {
  it("maps each diagram node to a React Flow node", () => {
    const { nodes } = diagramToFlow(makeDiagram());
    expect(nodes).toHaveLength(3);
    expect(nodes[0]).toMatchObject({
      id: "front",
      position: { x: 80, y: 240 },
      data: { label: "App", tangramType: "frontend" },
    });
  });

  it("maps each diagram edge to a React Flow edge", () => {
    const { edges } = diagramToFlow(makeDiagram());
    expect(edges).toHaveLength(2);
    expect(edges[0]).toMatchObject({ id: "e1", source: "front", target: "api" });
    expect(edges[1]).toMatchObject({ id: "e2", source: "api", target: "db" });
  });

  it("preserves backend-assigned positions", () => {
    const { nodes } = diagramToFlow(makeDiagram());
    const positions = nodes.map((n) => n.position);
    expect(positions).toEqual([
      { x: 80, y: 240 },
      { x: 560, y: 240 },
      { x: 800, y: 240 },
    ]);
  });

  it("stashes the original Tangram node in data.tangram", () => {
    const { nodes } = diagramToFlow(makeDiagram());
    expect(nodes[0].data?.tangram).toMatchObject({ id: "front", type: "frontend" });
  });
});
