import type { InputHTMLAttributes } from "react";
import { forwardRef } from "react";

import { cn } from "@/lib/utils";

export type InputProps = InputHTMLAttributes<HTMLInputElement>;

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "flex h-9 w-full rounded-[var(--radius)] border border-line bg-card px-3 text-sm",
        "text-ink-strong placeholder:text-ink-faint placeholder:font-mono placeholder:text-[12.5px]",
        "focus-visible:outline-none focus-visible:border-accent focus-visible:ring-2 focus-visible:ring-accent-tint",
        "disabled:cursor-not-allowed disabled:opacity-60",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";
