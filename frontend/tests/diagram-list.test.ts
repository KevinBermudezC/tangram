import { describe, expect, it } from "vitest";

import { toDiagramListItem } from "@/lib/diagram-list";
import type { DiagramSummary } from "@/types/tangram";

const summary: DiagramSummary = {
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  name: "Delivery app",
  description: null,
  createdAt: "2026-05-23T10:00:00Z",
  updatedAt: "2026-05-23T11:00:00Z",
  nodeCount: 4,
  edgeCount: 3,
  thumb: {
    nodes: [{ type: "frontend", x: 10, y: 10, w: 40, h: 24 }],
    edges: [],
  },
};

describe("toDiagramListItem()", () => {
  const now = new Date("2026-05-23T12:00:00Z");

  it("maps summary fields onto the card view model", () => {
    const item = toDiagramListItem(summary, now);
    expect(item.id).toBe(summary.id);
    expect(item.name).toBe("Delivery app");
    expect(item.components).toBe(4);
    expect(item.connections).toBe(3);
    expect(item.updatedLabel).toBe("1h ago");
    expect(item.thumb).toEqual(summary.thumb);
  });

  it("defaults source to ai because the backend does not track it", () => {
    expect(toDiagramListItem(summary, now).source).toBe("ai");
  });

  it("treats a non-Date second argument as wall-clock now (Array.map safety)", () => {
    const item = toDiagramListItem(summary, 0 as unknown as Date);
    expect(item.id).toBe(summary.id);
    expect(item.updatedLabel).toBeTruthy();
  });
});
