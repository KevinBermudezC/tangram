import Link from "next/link";

import { cn } from "@/lib/utils";

interface BrandProps {
  href?: string;
  className?: string;
  /** When true, the wordmark is hidden — useful inside collapsed sidebars. */
  iconOnly?: boolean;
}

/** Tiny brand mark + wordmark, shared by every app surface. */
export function Brand({ href = "/", className, iconOnly = false }: BrandProps) {
  return (
    <Link
      href={href}
      className={cn(
        "inline-flex items-center gap-2.5 text-ink-strong no-underline",
        className,
      )}
    >
      <span
        aria-hidden
        className="inline-flex h-6 w-6 items-center justify-center rounded-md bg-ink-strong text-[12px] font-bold text-ink-on-accent"
      >
        T
      </span>
      {!iconOnly && (
        <span className="text-[15px] font-semibold tracking-tight">
          Tangram
        </span>
      )}
    </Link>
  );
}
