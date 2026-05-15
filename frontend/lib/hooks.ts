"use client";

import { useMutation, useQuery } from "@tanstack/react-query";

import { generate, getHealth } from "@/lib/api";
import { recentDiagrams } from "@/lib/mock-data";
import type { MockDiagram } from "@/lib/mock-data";
import type { Diagram } from "@/types/tangram";

/**
 * Tangram backend hooks.
 *
 * Goal: every backend call goes through one of these, so caching, retries,
 * and error normalization live in a single layer. Components stay
 * declarative.
 *
 * Roadmap:
 *   - useHealth        → live now, polls /health
 *   - useGenerate      → live now, wraps POST /generate as a mutation
 *   - useDiagrams      → MOCK until `add-diagram-persistence-routes` lands
 *   - useDiagram(id)   → MOCK until same
 *   - useChat          → uses /api/chat (the local mock route) — switches
 *                        transparently when the real chat endpoint exists
 */

// --- Health probe -----------------------------------------------------------

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    // The backend is local — refresh every 20s so the rail badge reflects
    // an `uvicorn` restart within a sane delay without being noisy.
    refetchInterval: 20_000,
    refetchIntervalInBackground: false,
    retry: 0,
    staleTime: 15_000,
    // Don't blow up the rail if the backend is down; we want a soft badge.
    gcTime: 60_000,
  });
}

// --- Generate (POST /generate) ---------------------------------------------

export function useGenerate() {
  return useMutation<Diagram, Error, string>({
    mutationKey: ["generate"],
    mutationFn: (prompt) => generate(prompt),
  });
}

// --- Library (mocked) -------------------------------------------------------

/**
 * Mock-backed list of saved diagrams.
 *
 * Returns the same data the rail and library page hand-import today; it
 * exists as a hook now so the call site never knows it's mock, and the
 * day a `GET /diagrams` endpoint exists this body changes without
 * touching the components.
 */
export function useDiagrams() {
  return useQuery<MockDiagram[]>({
    queryKey: ["diagrams"],
    queryFn: async () => recentDiagrams,
    // No real network — the staleTime is just to prevent the
    // refetchInterval default from kicking in.
    staleTime: Infinity,
  });
}
