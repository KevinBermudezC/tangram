"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ThemeProvider } from "next-themes";
import { useState } from "react";
import type { ReactNode } from "react";
import { Toaster } from "sonner";

/**
 * Client-side providers mounted once at the root.
 *
 * - **TanStack Query**: every backend call goes through `useQuery` /
 *   `useMutation`. Keeps fetching, caching, retries, devtools in one
 *   place. Generation gets `retry: false` (LLM 5xx isn't worth
 *   auto-retrying; let the user see the error).
 * - **next-themes**: light / dark / system. Class strategy + localStorage
 *   (`tangram-theme`); default follows the OS.
 * - **Sonner**: toast notifications. We use it for transient feedback —
 *   "backend unreachable", "prompt copied", etc. — not for blocking
 *   errors, which still render inline.
 */
export function Providers({ children }: { children: ReactNode }) {
  // useState ensures the client is created once per component instance,
  // surviving HMR but not crossing requests in SSR.
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Don't auto-refetch on focus. The diagrams are stable while the
            // user is editing — we'd rather they keep their state than have
            // a refocus trigger a network call.
            refetchOnWindowFocus: false,
            // Short stale time + one retry is the right default for our
            // local-dev backend. The health probe overrides this for a
            // longer stale window.
            staleTime: 30_000,
            retry: 1,
          },
          mutations: {
            retry: false,
          },
        },
      }),
  );

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      storageKey="tangram-theme"
      disableTransitionOnChange
    >
      <QueryClientProvider client={client}>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "var(--color-card)",
              color: "var(--color-ink-strong)",
              border: "1px solid var(--color-line)",
            },
          }}
        />
        {/*
          React Query devtools — dev-only, bottom-right.

          `bottom-left` collided with the rail footer (BackendStatus + GitHub
          link), so the button got positioned on top of "Checking…" and
          "Pre-alpha". The right corner only competes with Next.js's own
          dev-mode indicator, which is fine.

          The library no-ops in production builds anyway, but we gate it
          explicitly so the bundle stays clean and there's no chance of a
          contributor seeing a stray devtools chip in a deployed preview.
        */}
        {process.env.NODE_ENV === "development" && (
          <ReactQueryDevtools
            initialIsOpen={false}
            buttonPosition="bottom-right"
          />
        )}
      </QueryClientProvider>
    </ThemeProvider>
  );
}
