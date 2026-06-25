import type { Edge, Node } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { autoLayout } from "@/lib/autoLayout";

const node = (id: string): Node => ({
  id,
  type: "tangram",
  position: { x: 0, y: 0 },
  data: { label: id, tangramType: "backend" },
});

describe("autoLayout", () => {
  it("returns an empty array unchanged", () => {
    expect(autoLayout([], [])).toEqual([]);
  });

  it("assigns a position to every node", () => {
    const nodes = [node("a"), node("b"), node("c")];
    const edges: Edge[] = [
      { id: "e1", source: "a", target: "b" },
      { id: "e2", source: "b", target: "c" },
    ];
    const out = autoLayout(nodes, edges);
    expect(out).toHaveLength(3);
    for (const n of out) {
      expect(Number.isFinite(n.position.x)).toBe(true);
      expect(Number.isFinite(n.position.y)).toBe(true);
    }
  });

  it("lays a chain out left-to-right (source before target)", () => {
    const nodes = [node("a"), node("b"), node("c")];
    const edges: Edge[] = [
      { id: "e1", source: "a", target: "b" },
      { id: "e2", source: "b", target: "c" },
    ];
    const byId = Object.fromEntries(
      autoLayout(nodes, edges).map((n) => [n.id, n.position.x]),
    );
    expect(byId.a).toBeLessThan(byId.b);
    expect(byId.b).toBeLessThan(byId.c);
  });

  it("preserves node identity and data", () => {
    const out = autoLayout([node("keep")], []);
    expect(out[0]).toMatchObject({ id: "keep", data: { label: "keep" } });
  });
});
