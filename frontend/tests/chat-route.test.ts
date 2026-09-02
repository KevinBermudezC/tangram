import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

describe("POST /api/chat passthrough", () => {
  const src = readFileSync(path.join(frontendRoot, "app/api/chat/route.ts"), "utf8");

  it("does not contain pickReply or canned keyword replies", () => {
    expect(src).not.toContain("pickReply");
    expect(src).not.toMatch(/lower\.includes\(["']auth["']\)/);
    expect(src).not.toMatch(/lower\.includes\(["']queue["']\)/);
    expect(src).not.toMatch(/lower\.includes\(["']cache["']\)/);
    expect(src).not.toContain("canned");
  });

  it("forwards the snapshot and selected_node_id to POST /chat", () => {
    expect(src).toContain("${API_BASE_URL}/chat");
    expect(src).toContain("selected_node_id");
    expect(src).toContain("diagram");
  });
});

describe("ChatPanel request body", () => {
  const src = readFileSync(
    path.join(frontendRoot, "components/editor/chat-panel.tsx"),
    "utf8",
  );

  it("sends the live snapshot and selected_node_id via chatContextBody", () => {
    expect(src).toContain("chatContextBody");
    expect(src).toContain("prepareSendMessagesRequest");
    expect(src).toContain("selectedNodeId: selectedNode?.id");
    expect(src).not.toContain("pickReply");
  });
});
