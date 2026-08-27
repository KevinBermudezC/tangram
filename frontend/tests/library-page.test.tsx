import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { DiagramListItem } from "@/lib/diagram-list";

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

vi.mock("@/components/templates-strip", () => ({
  TemplatesStrip: () => <div data-testid="templates-strip" />,
}));

const useDiagrams = vi.fn();
vi.mock("@/lib/hooks", () => ({
  useDiagrams: () => useDiagrams(),
}));

import LibraryPage from "@/app/(app)/library/page";

const item: DiagramListItem = {
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  name: "Delivery app",
  source: "ai",
  components: 4,
  connections: 3,
  updatedLabel: "1h ago",
  thumb: { nodes: [], edges: [] },
};

describe("LibraryPage", () => {
  it("renders saved diagrams as links to /editor/{id}", () => {
    useDiagrams.mockReturnValue({ data: [item], isLoading: false, isError: false });
    render(<LibraryPage />);
    const link = screen.getByRole("link", { name: /delivery app/i });
    expect(link).toHaveAttribute("href", `/editor/${item.id}`);
  });

  it("shows an empty-store message when there are no diagrams", () => {
    useDiagrams.mockReturnValue({ data: [], isLoading: false, isError: false });
    render(<LibraryPage />);
    expect(screen.getByText(/no saved diagrams yet/i)).toBeInTheDocument();
    expect(
      screen.queryByText(/couldn't load diagrams/i),
    ).not.toBeInTheDocument();
  });

  it("shows an error when GET /diagrams fails, not an empty store", () => {
    useDiagrams.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });
    render(<LibraryPage />);
    expect(screen.getByText(/couldn't load diagrams/i)).toBeInTheDocument();
    expect(screen.queryByText(/no saved diagrams yet/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /delivery app/i })).not.toBeInTheDocument();
  });

  it("shows a filter-miss message when diagrams exist but none match", async () => {
    const user = userEvent.setup();
    useDiagrams.mockReturnValue({ data: [item], isLoading: false, isError: false });
    render(<LibraryPage />);
    await user.type(screen.getByPlaceholderText(/search diagrams/i), "zzzz");
    expect(screen.getByText(/no diagrams match this filter yet/i)).toBeInTheDocument();
  });
});
