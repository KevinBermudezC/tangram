import { createUIMessageStream, createUIMessageStreamResponse } from "ai";
import type { UIMessage } from "ai";

/**
 * Mock chat endpoint.
 *
 * The real Tangram chat endpoint doesn't exist yet — it'll land with
 * `add-ai-explanation-panel` / a follow-up "chat about diagram" proposal.
 * Until then this route returns a streamed canned answer so the UI can be
 * exercised end-to-end (Streamdown + `useChat()` markdown rendering).
 *
 * What survives once the real endpoint lands:
 *   - the route at /api/chat
 *   - the UIMessage shape returned to the AI SDK client
 * What changes:
 *   - the body becomes a proxied call to Tangram backend's chat endpoint,
 *     streamed back via `createUIMessageStreamResponse` unchanged.
 */
export const runtime = "nodejs";

interface ChatRequest {
  messages: UIMessage[];
}

function pickReply(latest: string): string {
  const lower = latest.toLowerCase();
  if (lower.includes("auth") || lower.includes("login")) {
    return [
      "Two reasons most teams pull **Auth** out of the backend eventually:",
      "",
      "- **Blast radius.** Auth is the highest-value attack target. Isolating it makes it easier to audit, scale, and patch independently.",
      "- **Reuse.** Once you have a second backend or a mobile client, they all need to validate identity the same way — a dedicated service avoids duplicating that logic.",
      "",
      "> **Watch out:** direct database connections from the frontend are a security risk. Always go through the backend.",
      "",
      "For a small side project, folding auth into the backend is fine — you can split it later.",
    ].join("\n");
  }
  if (lower.includes("queue") || lower.includes("job")) {
    return [
      "A **queue** is worth adding when:",
      "",
      "1. You have work that takes longer than a request cycle (PDF generation, email sending, image processing).",
      "2. You need to retry on failure without blocking the user.",
      "3. You want to smooth bursty load — slow consumers + fast producers.",
      "",
      "Common shape: `Backend → Queue → Worker → Database`. Redis / SQS / RabbitMQ are all fine choices; pick by ops familiarity, not benchmarks.",
    ].join("\n");
  }
  if (lower.includes("cache")) {
    return [
      "Caches earn their keep when **reads vastly outnumber writes**.",
      "",
      "Two patterns worth knowing:",
      "",
      "- **Cache-aside**: app reads from cache; on miss, fetches from DB and writes the result back. Simple, widely understood.",
      "- **Write-through**: every DB write also updates the cache. Lower miss rate, but writes are slower.",
      "",
      "The hard part is always **invalidation**. If your data is rarely stale, TTLs work. If freshness matters, you need explicit invalidation events from the writer.",
    ].join("\n");
  }
  return [
    "Click any node in the canvas and ask me about it — I can explain what it is, why it's typically there, and what usually goes wrong.",
    "",
    "Try asking:",
    "",
    "- *Why is Auth on its own service?*",
    "- *When does this need a queue?*",
    "- *Should I add a cache here?*",
  ].join("\n");
}

function extractText(message: UIMessage): string {
  return (
    message.parts
      ?.filter((p) => p.type === "text")
      .map((p) => ("text" in p ? p.text : ""))
      .join(" ") ?? ""
  );
}

export async function POST(request: Request) {
  const body = (await request.json()) as ChatRequest;
  const last = body.messages.at(-1);
  const fullText = pickReply(last ? extractText(last) : "");

  // Tokenise so the response feels "typed", not pasted. Roughly word-sized.
  const chunks = fullText.match(/.{1,18}(\s|$)/g) ?? [fullText];

  const stream = createUIMessageStream({
    execute: async ({ writer }) => {
      const id = "msg-mock";
      writer.write({ type: "text-start", id });
      for (const chunk of chunks) {
        await new Promise((r) => setTimeout(r, 24));
        writer.write({ type: "text-delta", id, delta: chunk });
      }
      writer.write({ type: "text-end", id });
    },
  });

  return createUIMessageStreamResponse({ stream });
}
