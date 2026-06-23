import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  saveDiagram: vi.fn(async (d: unknown) => d),
}));

import { saveDiagram } from "@/lib/api";
import { useDiagramEditor } from "@/lib/useDiagramEditor";
import type { Diagram } from "@/types/tangram";

const base: Diagram = {
  version: "0.1.0",
  id: "diag-1",
  metadata: {
    name: "Test",
    description: null,
    createdAt: "2026-05-09T00:00:00Z",
    updatedAt: "2026-05-09T00:00:00Z",
  },
  nodes: [],
  edges: [],
  conversation: [],
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const node = (id: string, type: string): any => ({
  id,
  type: "tangram",
  position: { x: 0, y: 0 },
  data: { label: id, tangramType: type },
});

function makeWrapper() {
  const qc = new QueryClient({
    defaultOptions: { mutations: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  };
}

describe("useDiagramEditor", () => {
  beforeEach(() => {
    (saveDiagram as ReturnType<typeof vi.fn>).mockClear();
  });
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("does not persist on the initial seed report", async () => {
    const { result } = renderHook(() => useDiagramEditor(base), {
      wrapper: makeWrapper(),
    });

    // First onChange is the seed, not an edit.
    act(() => {
      result.current.onChange([node("a", "frontend")], []);
    });
    act(() => {
      result.current.saveNow();
    });

    await Promise.resolve();
    expect(saveDiagram).not.toHaveBeenCalled();
    expect(result.current.canSave).toBe(false);
  });

  it("persists the serialized graph after an edit + saveNow", async () => {
    const { result } = renderHook(() => useDiagramEditor(base), {
      wrapper: makeWrapper(),
    });

    // Seed, then a real edit (a second report with more nodes).
    act(() => {
      result.current.onChange([node("a", "frontend")], []);
    });
    act(() => {
      result.current.onChange(
        [node("a", "frontend"), node("b", "database")],
        [],
      );
    });
    expect(result.current.canSave).toBe(true);

    act(() => {
      result.current.saveNow();
    });

    await waitFor(() => expect(saveDiagram).toHaveBeenCalledTimes(1));
    const saved = (saveDiagram as ReturnType<typeof vi.fn>).mock
      .calls[0][0] as Diagram;
    expect(saved.id).toBe("diag-1");
    expect(saved.nodes.map((n) => n.id)).toEqual(["a", "b"]);
  });
});
