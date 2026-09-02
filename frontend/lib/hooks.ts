"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  analyze,
  generate,
  getDiagram,
  getHealth,
  listDiagrams,
  saveDiagram,
} from "@/lib/api";
import { toDiagramListItem, type DiagramListItem } from "@/lib/diagram-list";
import type { AnalyzeResponse, Diagram } from "@/types/tangram";

/**
 * Tangram backend hooks.
 *
 * Goal: every backend call goes through one of these, so caching, retries,
 * and error normalization live in a single layer. Components stay
 * declarative.
 *
 * Status:
 *   - useHealth        → polls /health
 *   - useGenerate      → wraps POST /generate as a mutation
 *   - useAnalyze       → wraps POST /analyze as a mutation (on-demand)
 *   - useDiagrams      → GET /diagrams (live), mapped to DiagramListItem
 *   - useDiagram(id)   → GET /diagrams/{id} (live)
 *   - useSaveDiagram   → POST /diagrams (live), invalidates the list
 *   - useChat          → /api/chat passthrough to POST /chat (inspect tools)
 */

const DIAGRAMS_KEY = ["diagrams"] as const;

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

// --- Analyze (POST /analyze) ------------------------------------------------

/** Run anti-pattern analysis + tutor feedback on a diagram, on demand. */
export function useAnalyze() {
  return useMutation<AnalyzeResponse, Error, { diagram: Diagram; modeId?: string }>({
    mutationKey: ["analyze"],
    mutationFn: ({ diagram, modeId }) => analyze(diagram, modeId),
  });
}

// --- Library (GET /diagrams) ------------------------------------------------

/** Live list of saved diagrams, newest first, shaped for the cards. */
export function useDiagrams() {
  return useQuery<DiagramListItem[]>({
    queryKey: DIAGRAMS_KEY,
    queryFn: async () => (await listDiagrams()).map((summary) => toDiagramListItem(summary)),
    staleTime: 10_000,
    // A down backend should surface as an error, not a long skeleton.
    retry: 0,
  });
}

/** Load one full diagram by id (for `/editor/[id]`). */
export function useDiagram(id: string | undefined) {
  return useQuery<Diagram>({
    queryKey: ["diagram", id],
    queryFn: () => getDiagram(id as string),
    enabled: Boolean(id),
    retry: 0,
  });
}

/** Persist a diagram, then refresh the library list. */
export function useSaveDiagram() {
  const queryClient = useQueryClient();
  return useMutation<Diagram, Error, Diagram>({
    mutationKey: ["save-diagram"],
    mutationFn: (diagram) => saveDiagram(diagram),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: DIAGRAMS_KEY });
    },
  });
}
