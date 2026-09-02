import type { Diagram } from "@/types/tangram";

/** Extra fields merged into the useChat POST /api/chat body. */
export function chatContextBody(opts: {
  diagram?: Diagram | null;
  selectedNodeId?: string | null;
}): {
  diagram: Diagram | null;
  diagram_id: string | null;
  selected_node_id: string | null;
} {
  return {
    diagram: opts.diagram ?? null,
    diagram_id: opts.diagram?.id ?? null,
    selected_node_id: opts.selectedNodeId ?? null,
  };
}
