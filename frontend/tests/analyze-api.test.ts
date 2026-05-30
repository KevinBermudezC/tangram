import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { analyze, TangramApiError } from "@/lib/api";
import type { AnalyzeResponse, Diagram } from "@/types/tangram";

const mockDiagram: Diagram = {
  version: "0.1.0",
  id: "abc",
  metadata: {
    name: "Test",
    description: null,
    createdAt: "2026-05-09T00:00:00Z",
    updatedAt: "2026-05-09T00:00:00Z",
  },
  nodes: [
    {
      id: "front",
      type: "frontend",
      label: "App",
      position: { x: 0, y: 0 },
      properties: {},
    },
    {
      id: "db",
      type: "database",
      label: "DB",
      position: { x: 200, y: 0 },
      properties: {},
    },
  ],
  edges: [
    {
      id: "e1",
      source: "front",
      target: "db",
      properties: {},
    },
  ],
  conversation: [],
};

const mockAnalysis: AnalyzeResponse = {
  findings: [
    {
      rule_id: "no-direct-frontend-to-database",
      severity: "error",
      message: "Frontend talks to the database directly.",
      rationale: "Put an API between them.",
      node_ids: ["front", "db"],
      edge_ids: ["e1"],
    },
  ],
  feedback: "Your frontend reaches the database directly; add a backend layer.",
};

describe("analyze()", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns findings and feedback on 200", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify(mockAnalysis), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const result = await analyze(mockDiagram);
    expect(result.feedback).toContain("backend layer");
    expect(result.findings).toHaveLength(1);
    expect(result.findings[0].rule_id).toBe("no-direct-frontend-to-database");
  });

  it("sends the diagram in the request body", async () => {
    const fetchMock = globalThis.fetch as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ findings: [], feedback: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await analyze(mockDiagram);

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/analyze");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toEqual({ diagram: mockDiagram });
  });

  it("includes modeId when provided", async () => {
    const fetchMock = globalThis.fetch as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ findings: [], feedback: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await analyze(mockDiagram, "senior");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toMatchObject({ modeId: "senior" });
  });

  it("throws TangramApiError with code on backend error", async () => {
    const makeResponse = () =>
      new Response(
        JSON.stringify({ detail: "Diagram exceeds the cap", code: "diagram_too_large" }),
        { status: 413, headers: { "Content-Type": "application/json" } },
      );
    (globalThis.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(makeResponse())
      .mockResolvedValueOnce(makeResponse());

    await expect(analyze(mockDiagram)).rejects.toThrowError(TangramApiError);
    await expect(analyze(mockDiagram)).rejects.toMatchObject({
      code: "diagram_too_large",
      status: 413,
    });
  });
});
