import { API_BASE_URL } from "@/lib/api";
import type { UIMessage } from "ai";

/**
 * Passthrough to FastAPI POST /chat.
 *
 * The tutor brain (modes/tutor.md, retrieval, inspect_diagram / inspect_node)
 * lives on the backend. This route only maps UIMessages and forwards the
 * live diagram snapshot + selected_node_id. No canned replies.
 */
export const runtime = "nodejs";

interface IncomingChatRequest {
  messages?: UIMessage[];
  diagram?: unknown;
  diagram_id?: string | null;
  diagramId?: string | null;
  selected_node_id?: string | null;
  selectedNodeId?: string | null;
}

function textOf(message: UIMessage): string {
  return (
    message.parts
      ?.filter((part) => part.type === "text")
      .map((part) => ("text" in part ? part.text : ""))
      .join("") ?? ""
  );
}

export async function POST(request: Request) {
  const body = (await request.json()) as IncomingChatRequest;
  const messages = (body.messages ?? [])
    .filter((message) => message.role === "user" || message.role === "assistant")
    .map((message) => ({
      role: message.role,
      content: textOf(message),
    }));

  const upstream = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      diagram: body.diagram ?? null,
      diagram_id: body.diagram_id ?? body.diagramId ?? null,
      selected_node_id: body.selected_node_id ?? body.selectedNodeId ?? null,
    }),
  });

  const headers = new Headers();
  const contentType = upstream.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);
  headers.set(
    "x-vercel-ai-ui-message-stream",
    upstream.headers.get("x-vercel-ai-ui-message-stream") ?? "v1",
  );
  headers.set("Cache-Control", "no-cache");

  return new Response(upstream.body, {
    status: upstream.status,
    headers,
  });
}
