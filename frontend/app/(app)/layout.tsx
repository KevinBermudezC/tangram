import type { ReactNode } from "react";

import { AppRail } from "@/components/app-rail";

/**
 * Shared shell for the in-app surfaces (Home, Library, future Templates +
 * Settings). The Editor uses its own full-width layout (no rail) so it
 * lives outside this segment.
 */
export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-[248px_1fr]">
      <AppRail />
      <div className="min-w-0">{children}</div>
    </div>
  );
}
