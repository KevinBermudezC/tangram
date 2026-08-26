import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

const setTheme = vi.fn();
let mockTheme: string | undefined = "system";

vi.mock("next-themes", () => ({
  useTheme: () => ({
    theme: mockTheme,
    setTheme,
  }),
}));

import { ThemeToggle } from "@/components/theme-toggle";

describe("ThemeToggle", () => {
  beforeEach(() => {
    setTheme.mockClear();
    mockTheme = "system";
  });

  it("cycles system → light on click once mounted", async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const button = await screen.findByRole("button", {
      name: /theme: system/i,
    });
    await user.click(button);

    expect(setTheme).toHaveBeenCalledWith("light");
  });

  it("shows dark aria when theme is dark", async () => {
    mockTheme = "dark";
    render(<ThemeToggle />);
    expect(
      await screen.findByRole("button", { name: /theme: dark/i }),
    ).toBeInTheDocument();
  });
});
