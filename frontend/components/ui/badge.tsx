import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full text-[9.5px] font-bold uppercase tracking-[0.1em] px-2 py-[3px]",
  {
    variants: {
      variant: {
        ai: "bg-accent text-ink-on-accent",
        manual: "bg-black/80 text-[#fffaf3]",
        draft: "bg-card text-ink-muted border border-line",
        pill: "bg-accent-tint text-accent-strong",
        outline: "border border-line text-ink-body bg-card",
      },
    },
    defaultVariants: { variant: "outline" },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}
