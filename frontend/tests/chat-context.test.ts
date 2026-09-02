import { describe, expect, it } from "vitest";

import { chatContextBody } from "@/lib/chat-request";
import { chipForToolPart, titleNodeType } from "@/lib/chat-tool-chip";
import type { Diagram } from "@/types/tangram";

const diagram: Diagram = {
  version: "0.1.0",
  id: "01HZZZZZZZZZZZZZZZZZZZZZZA",
  metadata: {
    name: "Delivery",
    description: null,
    createdAt: "2026-05-09T00:00:00Z",
    updatedAt: "2026-05-09T00:00:00Z",
  },
  nodes: [
    {
      id: "orders",
      type: "queue",
      label: "Orders",
      position: { x: 0, y: 0 },
      properties: {},
    },
  ],
  edges: [],
  conversation: [],
};

describe("chatContextBody", () => {
  it("sends live diagram and selected_node_id for an unsaved canvas", () => {
    expect(
      chatContextBody({ diagram, selectedNodeId: "orders" }),
    ).toEqual({
      diagram,
      diagram_id: diagram.id,
      selected_node_id: "orders",
    });
  });

  it("sends nulls when nothing is on the canvas", () => {
    expect(chatContextBody({})).toEqual({
      diagram: null,
      diagram_id: null,
      selected_node_id: null,
    });
  });
});

describe("chipForToolPart", () => {
  it("formats inspect_node as miró Type · label", () => {
    expect(
      chipForToolPart({
        type: "tool-inspect_node",
        state: "output-available",
        output: { type: "queue", label: "Orders" },
      }),
    ).toBe("miró Queue · Orders");
  });

  it("formats inspect_diagram", () => {
    expect(
      chipForToolPart({
        type: "tool-inspect_diagram",
        state: "output-available",
      }),
    ).toBe("miró diagram");
  });
});

describe("titleNodeType", () => {
  it("title-cases underscored types", () => {
    expect(titleNodeType("external_service")).toBe("External Service");
  });
});
