"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  analyze,
  chat as realChat,
  generate,
  getDiagram,
  getHealth,
  listDiagrams,
  saveDiagram,
  sendMessage,
} from "@/lib/api";
import { relativeTime } from "@/lib/format";
import type { MockDiagram } from "@/lib/mock-data";
import type {
  AnalyzeResponse,
  ChatMessage,
  Diagram,
  DiagramSummary,
} from "@/types/tangram";

/**
 * Tangram backend hooks.
 *
 * Goal: every backend call goes through one of these, so caching, retries,
 * and error normalization live in a single layer. Components stay
 * declarative.
 *
 * Status:
 *    - useHealth         → polls /health
 *    - useGenerate       → wraps POST /generate as a mutation
 *    - useAnalyze        → wraps POST /analyze as a mutation (on-demand)
 *    - useDiagrams       → GET /diagrams (live), mapped to the card view model
 *    - useDiagram(id)    → GET /diagrams/{id} (live)
 *    - useSaveDiagram    → POST /diagrams (live), invalidates the list
 *    - useChat           → uses /api/chat (real endpoint) for interactive chat
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

/**
 * Map a backend summary to the card/rail view model.
 *
 * `source` isn't tracked server-side yet; every persisted diagram today comes
 * from generation, so we label it "ai". The thumb geometry comes straight
 * from the backend projection.
 */
function summaryToCard(summary: DiagramSummary): MockDiagram {
  return {
    id: summary.id,
    name: summary.name,
    source: "ai",
    components: summary.nodeCount,
    connections: summary.edgeCount,
    updatedLabel: relativeTime(summary.updatedAt),
    thumb: summary.thumb,
   };
}

/** Live list of saved diagrams, newest first, shaped for the cards. */
export function useDiagrams() {
  return useQuery<MockDiagram[]>({
    queryKey: DIAGRAMS_KEY,
    queryFn: async () => (await listDiagrams()).map(summaryToCard),
    staleTime: 10_000,
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

// --- Chat ----------------------------------------------------------

/**
 * Use real chat from /api/chat endpoint.
 *
 * This is the interactive streaming endpoint that accepts conversation history
 * and new user input, returning a complete conversation with the assistant's reply appended.
 * The response is streamed incrementally so the frontend can render partial Markdown as it arrives.
 */
export function useChat() {
  return useMutation<ChatResponse, Error, ChatMessage[]>({
    mutationKey: ["chat"],
    mutationFn: (messages) => sendMessage(messages, "Hello, Tangram!"),
   });
}

/**
 * Use real chat for a specific diagram context.
 *
 * This endpoint is optimized for batch requests where the entire chat history has already
 * been persisted in the backend. It accepts messages + new user input and returns a complete
 * conversation with the assistant reply appended at the end.
 */
export function useDiagramChat(diagramId: string) {
  return useMutation<ChatResponse, Error, ChatMessage[]>({
    mutationKey: ["diagram-chat", diagramId],
    mutationFn: (messages) => sendDiagramChat(messages, "Hello, Tangram!", diagramId),
   });
}
