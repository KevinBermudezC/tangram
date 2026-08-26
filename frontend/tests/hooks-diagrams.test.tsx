import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  listDiagrams: vi.fn(),
  getDiagram: vi.fn(),
  saveDiagram: vi.fn(),
}));

import { getDiagram, listDiagrams, saveDiagram } from "@/lib/api";
import { useDiagram, useDiagrams, useSaveDiagram } from "@/lib/hooks";
import type { Diagram, DiagramSummary } from "@/types/tangram";

const summary: DiagramSummary = {
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  name: "Saved",
  description: null,
  createdAt: "2026-05-23T10:00:00Z",
  updatedAt: "2026-05-23T11:00:00Z",
  nodeCount: 3,
  edgeCount: 2,
  thumb: { nodes: [], edges: [] },
};

const diagram: Diagram = {
  version: "0.1.0",
  id: summary.id,
  metadata: {
    name: "Saved",
    description: null,
    createdAt: summary.createdAt,
    updatedAt: summary.updatedAt,
  },
  nodes: [],
  edges: [],
  conversation: [],
};

function makeWrapper() {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  };
}

describe("diagram persistence hooks", () => {
  beforeEach(() => {
    vi.mocked(listDiagrams).mockReset();
    vi.mocked(getDiagram).mockReset();
    vi.mocked(saveDiagram).mockReset();
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("useDiagrams maps GET /diagrams summaries into list items", async () => {
    vi.mocked(listDiagrams).mockResolvedValueOnce([summary]);
    const { result } = renderHook(() => useDiagrams(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(listDiagrams).toHaveBeenCalledTimes(1);
    expect(result.current.data).toEqual([
      expect.objectContaining({
        id: summary.id,
        name: "Saved",
        source: "ai",
        components: 3,
        connections: 2,
      }),
    ]);
  });

  it("useDiagrams returns an empty list when the store is empty", async () => {
    vi.mocked(listDiagrams).mockResolvedValueOnce([]);
    const { result } = renderHook(() => useDiagrams(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual([]);
  });

  it("useDiagrams surfaces an error when the list fetch fails", async () => {
    vi.mocked(listDiagrams).mockRejectedValue(new Error("backend down"));
    const { result } = renderHook(() => useDiagrams(), { wrapper: makeWrapper() });
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toMatchObject({ message: "backend down" });
  });

  it("useDiagram loads GET /diagrams/{id}", async () => {
    vi.mocked(getDiagram).mockResolvedValueOnce(diagram);
    const { result } = renderHook(() => useDiagram(summary.id), {
      wrapper: makeWrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(getDiagram).toHaveBeenCalledWith(summary.id);
    expect(result.current.data?.id).toBe(summary.id);
  });

  it("useSaveDiagram POSTs and invalidates the list", async () => {
    vi.mocked(saveDiagram).mockResolvedValueOnce(diagram);
    vi.mocked(listDiagrams).mockResolvedValue([]);
    const wrapper = makeWrapper();
    const { result } = renderHook(() => useSaveDiagram(), { wrapper });
    result.current.mutate(diagram);
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(saveDiagram).toHaveBeenCalledWith(diagram);
  });
});
