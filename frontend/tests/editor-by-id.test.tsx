import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TangramApiError } from "@/lib/api";
import type { Diagram } from "@/types/tangram";

vi.mock("next/link", () => ({
  default: ({
    href,
    children,
    ...props
  }: {
    href: string;
    children: React.ReactNode;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("@/components/DiagramCanvas", () => ({
  DiagramCanvas: () => <div data-testid="diagram-canvas" />,
}));

vi.mock("@/components/editor/editor-shell", () => ({
  EditorShell: ({
    content,
    diagramName,
  }: {
    content: React.ReactNode;
    diagramName: string;
  }) => (
    <div>
      <h1>{diagramName}</h1>
      {content}
    </div>
  ),
}));

const useDiagram = vi.fn();
vi.mock("@/lib/hooks", () => ({
  useDiagram: (...args: unknown[]) => useDiagram(...args),
  useAnalyze: () => ({
    data: null,
    isError: false,
    isPending: false,
    mutate: vi.fn(),
    error: null,
  }),
}));

vi.mock("@/lib/useDiagramEditor", () => ({
  useDiagramEditor: () => ({
    onChange: vi.fn(),
    saveNow: vi.fn(),
    label: "—",
    canSave: false,
  }),
}));

import { EditorById } from "@/app/editor/[id]/page";

const diagram: Diagram = {
  version: "0.1.0",
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  metadata: {
    name: "Delivery app",
    description: null,
    createdAt: "2026-05-23T10:00:00Z",
    updatedAt: "2026-05-23T11:00:00Z",
  },
  nodes: [],
  edges: [],
  conversation: [],
};

function renderPage() {
  return render(<EditorById id={diagram.id} />);
}

describe("EditorByIdPage", () => {
  it("renders a loaded diagram on the canvas", async () => {
    useDiagram.mockReturnValue({
      data: diagram,
      isLoading: false,
      isError: false,
      error: null,
    });
    renderPage();
    expect(await screen.findByTestId("diagram-canvas")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /delivery app/i })).toBeInTheDocument();
  });

  it("shows a not-found state on typed 404", async () => {
    useDiagram.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new TangramApiError(404, {
        detail: "missing",
        code: "diagram_not_found",
      }),
    });
    renderPage();
    expect(await screen.findByText(/diagram not found/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /back to library/i })).toHaveAttribute(
      "href",
      "/library",
    );
    expect(screen.queryByTestId("diagram-canvas")).not.toBeInTheDocument();
  });

  it("shows a generic load error when the backend is down", async () => {
    useDiagram.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("network"),
    });
    renderPage();
    expect(await screen.findByText(/couldn't load diagram/i)).toBeInTheDocument();
    expect(screen.queryByText(/diagram not found/i)).not.toBeInTheDocument();
  });
});
