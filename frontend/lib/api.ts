import type { ApiErrorBody, Diagram } from "@/types/tangram";

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

/** POST /generate. Throws TangramApiError on non-2xx. */
export async function generate(prompt: string): Promise<Diagram> {
  const response = await fetch(`${API_BASE_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    let body: ApiErrorBody;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      body = {
        detail: `Backend returned ${response.status} with non-JSON body`,
        code: "unknown_error",
      };
    }
    // FastAPI's default 422 returns `{detail: [...]}` not `{detail, code}`.
    // Normalize so callers always see a string + a code.
    const normalized: ApiErrorBody = {
      detail:
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail),
      code: body.code ?? "validation_error",
    };
    throw new TangramApiError(response.status, normalized);
  }

  return (await response.json()) as Diagram;
}
