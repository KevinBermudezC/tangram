import type { HTMLAttributes } from "react";
import { forwardRef } from "react";

import { cn } from "@/lib/utils";

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        "rounded-[var(--radius-lg)] border border-line bg-card shadow-[0_1px_2px_rgba(26,26,26,0.04),0_1px_1px_rgba(26,26,26,0.03)]",
        className,
      )}
      {...props}
    />
  ),
);
Card.displayName = "Card";
