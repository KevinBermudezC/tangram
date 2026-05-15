import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PromptForm } from "@/components/PromptForm";

describe("PromptForm", () => {
  it("renders a textarea and a button", () => {
    render(<PromptForm onSubmit={vi.fn()} loading={false} />);
    expect(screen.getByLabelText(/describe a system/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /generate diagram/i })).toBeInTheDocument();
  });

  it("disables submit when textarea is empty", () => {
    render(<PromptForm onSubmit={vi.fn()} loading={false} />);
    const button = screen.getByRole("button", { name: /generate diagram/i });
    expect(button).toBeDisabled();
  });

  it("calls onSubmit with the trimmed prompt", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<PromptForm onSubmit={onSubmit} loading={false} />);

    const textarea = screen.getByLabelText(/describe a system/i);
    await user.type(textarea, "  delivery app  ");
    await user.click(screen.getByRole("button", { name: /generate diagram/i }));

    expect(onSubmit).toHaveBeenCalledWith("delivery app");
  });

  it("shows loading state and disables interaction while loading", () => {
    render(<PromptForm onSubmit={vi.fn()} loading={true} />);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent(/generating/i);
    expect(button).toBeDisabled();
  });
});
