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
      <span aria-hidden className="seal h-6 w-6 text-[13px]">
        巧
      </span>
      {!iconOnly && (
        <span className="font-serif text-[16px] font-semibold tracking-[0.14em] text-ink-strong">
          TANGRAM
        </span>
      )}
    </Link>
  );
}
