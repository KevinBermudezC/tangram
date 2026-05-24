import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  deleteDiagram,
  getDiagram,
  listDiagrams,
  saveDiagram,
  TangramApiError,
} from "@/lib/api";
import type { Diagram, DiagramSummary } from "@/types/tangram";

const mockDiagram: Diagram = {
  version: "0.1.0",
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  metadata: {
    name: "Saved",
    description: null,
    createdAt: "2026-05-09T00:00:00Z",
    updatedAt: "2026-05-09T00:00:00Z",
  },
  nodes: [],
  edges: [],
  conversation: [],
};

const mockSummary: DiagramSummary = {
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  name: "Saved",
  description: null,
  createdAt: "2026-05-09T00:00:00Z",
  updatedAt: "2026-05-09T00:00:00Z",
  nodeCount: 3,
  edgeCount: 2,
  thumb: { nodes: [], edges: [] },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("diagram persistence api", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("listDiagrams() returns the parsed summaries", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      jsonResponse([mockSummary]),
    );
    const result = await listDiagrams();
    expect(result).toHaveLength(1);
    expect(result[0].nodeCount).toBe(3);
  });

  it("getDiagram() returns the full diagram", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      jsonResponse(mockDiagram),
    );
    const result = await getDiagram(mockDiagram.id);
    expect(result.metadata.name).toBe("Saved");
  });

  it("getDiagram() throws a typed 404", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      jsonResponse({ detail: "nope", code: "diagram_not_found" }, 404),
    );
    await expect(getDiagram("01HZZZZZZZZZZZZZZZZZZZZZZZ")).rejects.toMatchObject({
      code: "diagram_not_found",
      status: 404,
    });
  });

  it("saveDiagram() POSTs and returns the stored diagram", async () => {
    const fetchMock = globalThis.fetch as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(mockDiagram, 201));
    const result = await saveDiagram(mockDiagram);
    expect(result.id).toBe(mockDiagram.id);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/diagrams"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("deleteDiagram() resolves on 204", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(null, { status: 204 }),
    );
    await expect(deleteDiagram(mockDiagram.id)).resolves.toBeUndefined();
  });

  it("deleteDiagram() throws on 404", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      jsonResponse({ detail: "nope", code: "diagram_not_found" }, 404),
    );
    await expect(deleteDiagram("01HZZZZZZZZZZZZZZZZZZZZZZZ")).rejects.toBeInstanceOf(
      TangramApiError,
    );
  });
});
