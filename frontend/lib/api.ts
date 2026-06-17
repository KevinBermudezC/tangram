import type {
  AnalyzeResponse,
  ApiErrorBody,
  ChatMessage,
  ChatResponse,
  Diagram,
  DiagramSummary,
} from "@/types/tangram";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Shape of `GET /health`. The backend returns `{status: "ok"}`. */
export interface HealthResponse {
  status: string;
  app?: string;
  version?: string;
}

/** GET /health. Throws on non-2xx or network failure. */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    // Short timeout via AbortSignal — health should be instant.
    signal: AbortSignal.timeout(2_500),
  });
  if (!response.ok) {
    throw new Error(`Health check returned ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

/** Typed error mirroring the backend's `{detail, code}` shape. */
export class TangramApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly detail: string;

  constructor(status: number, body: ApiErrorBody) {
    super(`[${body.code}] ${body.detail}`);
    this.name = "TangramApiError";
    this.status = status;
    this.code = body.code;
    this.detail = body.detail;
  }
}

/**
 * Throw a normalized TangramApiError for a non-2xx response.
 *
 * FastAPI's typed errors are `{detail, code}`, but its default 422 is
 * `{detail: [...]}`. Normalize both so every caller sees a string + a code.
 */
async function throwApiError(response: Response): Promise<never> {
  let body: ApiErrorBody;
  try {
    body = (await response.json()) as ApiErrorBody;
  } catch {
    body = {
      detail: `Backend returned ${response.status} with non-JSON body`,
      code: "unknown_error",
    };
  }
  throw new TangramApiError(response.status, {
    detail:
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail),
    code: body.code ?? "validation_error",
  });
}

/** POST /generate. Throws TangramApiError on non-2xx. */
export async function generate(prompt: string): Promise<Diagram> {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!response.ok) await throwApiError(response);
  return (await response.json()) as Diagram;
}

/**
 * POST /analyze. Send an existing diagram, get deterministic rule findings
 * plus an LLM prose critique. Read-only — never persists. Throws
 * TangramApiError on non-2xx.
 */
export async function analyze(
  diagram: Diagram,
  modeId?: string,
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(modeId ? { diagram, modeId } : { diagram }),
  });
  if (!response.ok) await throwApiError(response);
  return (await response.json()) as AnalyzeResponse;
}

// --- Chat API (/api/chat) ----------------------------------------------------

/** Interactive chat with streaming responses. */
export async function sendMessage(
  messages: ChatMessage[],
  userInput: string,
): Promise<ChatResponse> {
  const body = JSON.stringify({
    messages,
    user_input: userInput,
  });

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });

  if (!response.ok) await throwApiError(response);
  return (await response.json()) as ChatResponse;
}

/** Batch chat for a specific diagram with full context. */
export async function sendDiagramChat(
  messages: ChatMessage[],
  userInput: string,
  diagramId: string,
): Promise<ChatResponse> {
  const body = JSON.stringify({
    messages,
    user_input: userInput,
  });

  const response = await fetch(
    `${API_BASE_URL}/diagrams/${diagramId}/chat/messages`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    }
  );

  if (!response.ok) await throwApiError(response);
  return (await response.json()) as ChatResponse;
}

// --- Diagram persistence (/diagrams) ----------------------------------------

/** GET /diagrams. Lightweight summaries, newest first. */
export async function listDiagrams(): Promise<DiagramSummary[]> {
  const response = await fetch(`${API_BASE_URL}/diagrams`);
  if (!response.ok) await throwApiError(response);
  return (await response.json()) as DiagramSummary[];
}

/** GET /diagrams/{id}. Full diagram, or throws a 404 TangramApiError. */
export async function getDiagram(id: string): Promise<Diagram> {
  const response = await fetch(`${API_BASE_URL}/diagrams/${id}`);
  if (!response.ok) await throwApiError(response);
  return (await response.json()) as Diagram;
}

/** POST /diagrams. Persists a diagram and returns its stored form. */
export async function saveDiagram(diagram: Diagram): Promise<Diagram> {
  const response = await fetch(`${API_BASE_URL}/diagrams`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(diagram),
  });
  if (!response.ok) await throwApiError(response);
  return (await response.json()) as Diagram;
}

/** DELETE /diagrams/{id}. Resolves on 204; throws on 404. */
export async function deleteDiagram(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/diagrams/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) await throwApiError(response);
}
