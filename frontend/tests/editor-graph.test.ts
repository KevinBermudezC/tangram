import type { Connection, Edge } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { connectEdge, createNode } from "@/lib/editor-graph";

const conn = (source: string, target: string): Connection => ({
  source,
  target,
  sourceHandle: null,
  targetHandle: null,
});

describe("connectEdge", () => {
  it("appends an edge with a generated id for a valid connection", () => {
    const result = connectEdge([], conn("a", "b"));
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({ source: "a", target: "b" });
    expect(result[0].id).toBeTruthy();
  });

  it("rejects self-loops (returns the same array)", () => {
    const edges: Edge[] = [];
    const result = connectEdge(edges, conn("a", "a"));
    expect(result).toBe(edges);
  });

  it("rejects a duplicate source→target pair", () => {
    const first = connectEdge([], conn("a", "b"));
    const second = connectEdge(first, conn("a", "b"));
    expect(second).toBe(first);
    expect(second).toHaveLength(1);
  });

  it("allows the reverse direction as a distinct edge", () => {
    const first = connectEdge([], conn("a", "b"));
    const second = connectEdge(first, conn("b", "a"));
    expect(second).toHaveLength(2);
  });
});

describe("createNode", () => {
  it("builds a typed tangram node with a default label and unique id", () => {
    const node = createNode("database", { x: 120, y: 40 });
    expect(node).toMatchObject({
      type: "tangram",
      position: { x: 120, y: 40 },
      data: { tangramType: "database", label: "Database" },
    });
    expect(node.id).toContain("database-");
  });

  it("mints distinct ids across calls", () => {
    const a = createNode("cache", { x: 0, y: 0 });
    const b = createNode("cache", { x: 0, y: 0 });
    expect(a.id).not.toBe(b.id);
  });
});
