/**
 * Card/rail view model for saved diagrams.
 *
 * `GET /diagrams` returns `DiagramSummary`. Library cards and the rail Recent
 * list need a slightly richer shape (formatted relative time, counts, a
 * client-side source badge). Keep that mapping here — not in `mock-data.ts`.
 */

import { relativeTime } from "@/lib/format";
import type { DiagramSummary, DiagramThumb } from "@/types/tangram";

export type DiagramSource = "ai" | "manual" | "draft";

export interface DiagramListItem {
  id: string;
  name: string;
  source: DiagramSource;
  components: number;
  connections: number;
  updatedLabel: string;
  thumb: DiagramThumb;
}

/**
 * Map a backend summary to the card/rail view model.
 *
 * `source` isn't tracked server-side yet; every persisted diagram today comes
 * from generation or the editor, so we label it "ai".
 */
export function toDiagramListItem(
  summary: DiagramSummary,
  now: Date = new Date(),
): DiagramListItem {
  const clock = now instanceof Date ? now : new Date();
  return {
    id: summary.id,
    name: summary.name,
    source: "ai",
    components: summary.nodeCount,
    connections: summary.edgeCount,
    updatedLabel: relativeTime(summary.updatedAt, clock),
    thumb: summary.thumb,
  };
}
