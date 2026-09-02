## Why

The editor's right-rail tutor already speaks AI SDK + Streamdown against `/api/chat`, but that route is `pickReply`: keyword canned answers. A junior who selects a queue and asks "why is there a queue here?" gets a generic lecture, not an answer about *that* node. That is the anti-Tangram. This is roadmap MVP item #17 / GitHub issue #19. Analyze stays the existing button; this change is conversational inspection of the canvas.

## What Changes

- Add `POST /chat` on the FastAPI backend. Body: `{ messages, diagram?, diagram_id?, selected_node_id? }`. Inference stays here: `modes/tutor.md`, retrieval, BYOK/Ollama via `LLMProvider`. The tutor has exactly two tools, `inspect_diagram` and `inspect_node`, executed against the request snapshot (live `diagram` wins; else `diagram_id`). The handler streams the **UI Message Stream** protocol the rail already consumes, including tool parts. The diagram JSON is **not** stuffed into the system prompt; the model must inspect via tools.
- Replace `frontend/app/api/chat/route.ts` with a passthrough to `POST /chat`. Delete `pickReply` and every keyword canned reply. `useChat` still talks to `/api/chat`.
- `ChatPanel` sends the live diagram snapshot and `selected_node_id` on every turn (unsaved canvas works). Canvas selection is wired into the rail. Tool parts render as a minimal chip (`miró Queue · orders`).
- If there is no diagram (or no node when the question needs one), the tutor says so and asks for context. It does not invent boxes.

This proposal does **not**:

- Persist the thread onto `Diagram.conversation`.
- Add Vercel hosting, Vercel env vars, or a Vercel deployment.
- Change `/generate`, `/analyze`, persistence, or the editor chrome beyond selection → chat.
- Register `analyze` / `generate` as chat tools. Analyze stays the existing button.
- Run a second tutor prompt in Next.js (`streamText` as a brain). Next is a passthrough.
- Per-node explanation panel, Mermaid, dark mode, Cmd-K, OpenAPI codegen, rail redesign, senior/brainstorm modes.

## Capabilities

### New Capabilities

- `chat-about-diagram`: Conversational tutor over the open canvas. Covers FastAPI `POST /chat` (tutor + retrieval + `inspect_diagram` / `inspect_node` + UI Message Stream), the Next.js `/api/chat` passthrough, and rail wiring (snapshot + selected node + optional tool chip).

### Modified Capabilities

- `llm-providers`: `LLMProvider` gains `stream_parts` so chat can receive native tool-call parts. `generate` / `generate_structured` / `stream` stay unchanged.

## Impact

- **Code**: chat request schema; `app/services/chat/` (compose, tools, UI Message Stream, tool loop); `POST /chat`; `stream_parts` on adapters + FakeLLM; Next `/api/chat` passthrough; ChatPanel + canvas selection; tests.
- **Dependencies**: none new. No `@ai-sdk/openai` in Next — the brain is FastAPI.
- **Configuration**: no new env vars.
- **Documentation**: `POST /chat` in `backend/README.md`; frontend chat section; ROADMAP #17.
- **Secrets**: none. BYOK stays in `backend/.env`.
