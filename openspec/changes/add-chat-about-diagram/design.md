## Context

See proposal.md for motivation. Constraints that shape this design:

- `useChat` already consumes UI Message Stream from `/api/chat`. The mock uses `createUIMessageStream` + `pickReply`.
- `compose_prompt` injects full diagram JSON into the user message when a diagram is passed. Product forbids stuffing that JSON into the chat prompt; chat must not call `compose_prompt(..., diagram=the_snapshot)`.
- `LLMProvider.stream()` is text-only. Chat needs native tool-call parts → `stream_parts`.
- Product lock: visible tools + **brain on the backend**. Next.js must not run a second tutor prompt (`streamText` as orchestrator is rejected).
- Analyze remains the existing button. Chat tools are only `inspect_diagram` and `inspect_node`.

## Goals / Non-Goals

**Goals:**

- FastAPI `POST /chat` owns tutor composition (no diagram dump), retrieval, the two inspect tools, the tool loop, and UI Message Stream.
- Next `/api/chat` is a byte-passthrough (plus UIMessage → `{role, content}` mapping).
- Unsaved canvas: body carries `diagram` + `selected_node_id`.
- Selecting a queue/cache and asking why it is there yields an answer grounded in `inspect_node` (name, connections, why it is here).

**Non-Goals:**

- `streamText` / `tool()` in Next.js as the brain.
- Chat tools for analyze or generate.
- Persisting the thread.
- Dumping a "compact snapshot" into the system prompt as a substitute for tools.

## Decisions

### Brain on FastAPI; Next is a passthrough

```
useChat → POST /api/chat (Next, maps UIMessages, forwards snapshot + selected_node_id)
        → POST /chat (FastAPI: tutor + retrieval + inspect_* tools + UI Message Stream)
```

**Rejected: `streamText` + `tool()` in Next** with `@ai-sdk/openai` pointed at FastAPI. That is a second brain (Next owns the tool loop and would need its own system prompt). Product: inference stays in the backend.

**Rejected: dump compact node/edge lists into the system prompt** so the model can answer without tools. Product: do not stuff the JSON in secret; tools must be visible in the UI Message Stream.

Tool calling still uses **native** provider tools (`stream_parts`), not a homemade `{ "function": ... }` prose format. The wire format to the rail is the AI SDK UI Message Stream (the same protocol `streamText` would emit).

### Exactly two tools, executed on the snapshot

| Tool | Input | Result |
| --- | --- | --- |
| `inspect_diagram` | none | `{ nodes: [{id, type, label}], edges: [{id, source, target, label}] }` or `{ error: "no_diagram" }` |
| `inspect_node` | `{ node_id }` | node + incident edges, or `{ error: "unknown_node" }` / `{ error: "no_diagram" }` |

Live `diagram` wins over `diagram_id`. Tools never hit `/analyze` or `/generate`.

### Prompt: tutor + retrieval + tool instructions; no diagram dump

`compose_prompt(last_user_text, diagram=None)` so vocabulary + patterns land and the diagram JSON / findings dump does not. Then append:

- Tool instructions (`inspect_diagram`, `inspect_node`).
- If `selected_node_id` is set: that id only ("call `inspect_node` with this id; do not guess name/type").
- If unset: no node selected; if the user says "this"/"here", ask them to click a node; `inspect_diagram` is still allowed.
- Never invent nodes.

Client `system` turns are dropped. Conversation is the remaining user/assistant/tool turns.

### No diagram → deterministic refusal

If there is no live snapshot and no loadable `diagram_id`, do **not** call the LLM. Stream a short tutor message: no diagram, generate or open one, then select a node. That is how we guarantee "does not invent boxes."

Unknown `diagram_id` with no live snapshot → 404 `diagram_not_found` (same as `GET /diagrams/{id}`).

### UI Message Stream from FastAPI

Events: `start`, `text-start` / `text-delta` / `text-end`, `tool-input-start`, `tool-input-available`, `tool-output-available`, `finish`, then `data: [DONE]`. Header `x-vercel-ai-ui-message-stream: v1`. Next copies the stream to the browser.

Tool loop cap: 5 steps so a confused model cannot spin.

### Rail: snapshot + selection + optional chip

`DiagramCanvas` reports selection. Both editor pages pass `{ diagram, selectedNode }` into `ChatPanel`. `DefaultChatTransport` body: `{ diagram, diagram_id, selected_node_id }`. Chip for a finished `inspect_node`: `miró {Type} · {label}` (e.g. `miró Queue · Orders`). No rail redesign.

## Risks / Trade-offs

- **Risk**: small Ollama models skip tools. → **Mitigation**: tool instructions are explicit; tests fake a tool call then a grounded answer. Real-model quality is BYOK/Ollama's problem; the contract is "no canned reply, no secret dump."
- **Risk**: UI Message Stream field names drift vs `@ai-sdk/react`. → **Mitigation**: match the events `createUIMessageStream` already emitted in the mock (`text-start` / `text-delta` / `text-end`) plus documented tool parts.
- **Trade-off**: no compact snapshot in the prompt means every useful answer needs a tool call (visible, as required).

## Migration Plan

No migration. Rollback = revert. `/api/chat` URL unchanged.

## Open Questions

None.
