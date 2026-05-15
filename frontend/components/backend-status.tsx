"use client";

import { useHealth } from "@/lib/hooks";
import { cn } from "@/lib/utils";

/**
 * Pill-sized indicator that pings `/health` every 20s. Three states:
 *
 *   - up        (green dot, "Backend up")
 *   - down      (red dot, "Backend down — start uvicorn?")
 *   - checking  (faint dot, "Checking…") — only on the first ever render
 *
 * Lives in the rail's footer so contributors don't have to open DevTools
 * to know whether their local backend is reachable.
 */
export function BackendStatus() {
  const { data, isError, isLoading } = useHealth();

  const state: "up" | "down" | "checking" = isLoading
    ? "checking"
    : isError
      ? "down"
      : data?.status === "ok"
        ? "up"
        : "down";

  const label =
    state === "up"
      ? "Backend up"
      : state === "down"
        ? "Backend offline"
        : "Checking…";

  return (
    <span
      role="status"
      aria-live="polite"
      title={
        state === "down"
          ? `Backend at ${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} not reachable. Is uvicorn running?`
          : label
      }
      className="inline-flex items-center gap-2 py-0.5 text-[11px] text-ink-faint"
    >
      <span
        aria-hidden
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          state === "up" && "bg-[#3f6024]",
          state === "down" && "bg-[#a94f29]",
          state === "checking" && "bg-ink-faint",
        )}
      />
      {label}
    </span>
  );
}
