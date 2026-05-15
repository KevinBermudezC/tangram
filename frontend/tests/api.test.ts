import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { generate, TangramApiError } from "@/lib/api";
import type { Diagram } from "@/types/tangram";

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
      id: "n1",
      type: "frontend",
      label: "App",
      position: { x: 0, y: 0 },
      properties: {},
    },
  ],
  edges: [],
  conversation: [],
};

describe("generate()", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the parsed Diagram on 200", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify(mockDiagram), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const result = await generate("hello");
    expect(result.id).toBe("abc");
    expect(result.nodes).toHaveLength(1);
  });

  it("throws TangramApiError with code on backend error", async () => {
    // Each call to generate() consumes one mocked Response. Two asserts -> two mocks.
    const makeResponse = () =>
      new Response(
        JSON.stringify({ detail: "OPENAI_API_KEY is required", code: "llm_config_error" }),
        { status: 503, headers: { "Content-Type": "application/json" } },
      );
    (globalThis.fetch as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(makeResponse())
      .mockResolvedValueOnce(makeResponse());

    await expect(generate("hello")).rejects.toThrowError(TangramApiError);
    await expect(generate("hello")).rejects.toMatchObject({
      code: "llm_config_error",
      status: 503,
    });
  });

  it("normalizes FastAPI 422 (list detail) into a string", async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: [{ msg: "Field required" }] }), {
        status: 422,
        headers: { "Content-Type": "application/json" },
      }),
    );

    try {
      await generate("");
      expect.fail("should have thrown");
    } catch (err) {
      expect(err).toBeInstanceOf(TangramApiError);
      const e = err as TangramApiError;
      expect(e.code).toBe("validation_error");
      expect(typeof e.detail).toBe("string");
    }
  });
});
