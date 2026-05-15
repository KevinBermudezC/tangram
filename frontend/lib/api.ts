import type { ApiErrorBody, Diagram } from "@/types/tangram";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
