import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { DiagramListItem } from "@/lib/diagram-list";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

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

const useDiagrams = vi.fn();
vi.mock("@/lib/hooks", () => ({
  useDiagrams: () => useDiagrams(),
  useHealth: () => ({ data: { status: "ok" }, isError: false, isLoading: false }),
}));

import { AppRail } from "@/components/app-rail";

const item: DiagramListItem = {
  id: "01HXXXXXXXXXXXXXXXXXXXXXXX",
  name: "Delivery app",
  source: "ai",
  components: 4,
  connections: 3,
  updatedLabel: "1h ago",
  thumb: { nodes: [], edges: [] },
};

describe("AppRail Recent", () => {
  it("lists saved diagrams linking to /editor/{id}", () => {
    useDiagrams.mockReturnValue({ data: [item], isLoading: false, isError: false });
    render(<AppRail />);
    const link = screen.getByRole("link", { name: /delivery app/i });
    expect(link).toHaveAttribute("href", `/editor/${item.id}`);
  });

  it("shows an empty-store message when there are no diagrams", () => {
    useDiagrams.mockReturnValue({ data: [], isLoading: false, isError: false });
    render(<AppRail />);
    expect(screen.getByText(/no diagrams yet/i)).toBeInTheDocument();
    expect(
      screen.queryByText(/couldn't load recent/i),
    ).not.toBeInTheDocument();
  });

  it("shows an error when GET /diagrams fails, not an empty store", () => {
    useDiagrams.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });
    render(<AppRail />);
    expect(screen.getByText(/couldn't load recent/i)).toBeInTheDocument();
    expect(screen.queryByText(/no diagrams yet/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /delivery app/i })).not.toBeInTheDocument();
  });
});
