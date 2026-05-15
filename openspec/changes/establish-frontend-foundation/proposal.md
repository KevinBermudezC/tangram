## Why

The backend can generate a Diagram from a prompt. Today the only way to see that is to read JSON in a terminal. This proposal puts a real web UI in front of it: type a prompt, click a button, see the diagram rendered visually.

This is the first **demo moment** of the project. Up to now everything has been engineer-facing (curl, tests, logs). After this lands, anyone with two terminals can run Tangram and produce a real screenshot.

Scope is deliberately narrow: a **read-only** diagram viewer. The user types a prompt, hits generate, and the result is rendered with React Flow. Editing (drag, drop, connect, edit labels) is the next proposal (`add-diagram-editor`). Persistence, the explanation panel, and other polish ship in their own proposals.

## What Changes

- Add a `frontend/` workspace at the repo root with:
  - Next.js 15 (App Router) + TypeScript strict mode.
  - Tailwind CSS for styling.
  - React Flow (`@xyflow/react`) for the diagram canvas.
  - Vitest + Testing Library for tests.
  - ESLint via `eslint-config-next`.
- A single page (`app/page.tsx`) that:
  - Has a textarea for the user prompt.
  - Has a Generate button that POSTs to `/generate`.
  - Shows loading state while waiting.
  - Renders the returned `Diagram` in a read-only React Flow canvas.
  - Surfaces typed errors using the `code` field from the backend's error body.
- Hand-written TypeScript types in `frontend/types/tangram.ts` mirroring the backend Pydantic schemas. The future `add-openapi-typescript-codegen` proposal replaces these with auto-generated equivalents; the call sites do not change.
- An adapter `frontend/lib/diagramToFlow.ts` that converts a Tangram `Diagram` into the React Flow `nodes` / `edges` shape.
- An API client `frontend/lib/api.ts` with typed error handling.
- A `frontend/README.md` documenting setup, commands, and the `NEXT_PUBLIC_API_URL` env var.
- CI workflow extension: a new `frontend` job that runs `npm ci`, `npm run lint`, `npm run typecheck`, `npm run test` on every PR.
- Top-level `README.md` quick-start gains a frontend section.

This proposal does **not** add:
- Editing the diagram (drag, drop, connect, edit labels) — `add-diagram-editor` proposal.
- Saving / loading diagrams — `add-diagram-persistence-routes` + a frontend follow-up.
- The per-node AI explanation panel — `add-ai-explanation-panel`.
- OpenAPI codegen — `add-openapi-typescript-codegen`. For now we hand-write TypeScript types and accept the maintenance cost.

## Capabilities

### New Capabilities

- `frontend-foundation`: A Next.js + React Flow application that consumes `POST /generate`, renders the returned diagram visually (read-only), and surfaces typed errors. Defines the TypeScript type shape that mirrors the backend Pydantic schemas, the API client contract, the diagram → React Flow adapter, and the project's testing/linting toolchain.

### Modified Capabilities

- `continuous-integration`: CI gains a new `frontend` job that runs alongside the existing `lint`, `test`, `openspec` jobs.

## Impact

- **Code**: new `frontend/` directory at the repo root with ~30 new files. New CI job. No backend changes.
- **Dependencies**: Node.js 20+ becomes a development requirement for anyone working on the frontend. Backend-only contributors are unaffected.
- **Configuration**: one new env var (`NEXT_PUBLIC_API_URL`, defaults to `http://localhost:8000`).
- **Documentation**: `frontend/README.md` (new); top-level README quick-start expanded.
- **Future proposals unblocked**: `add-diagram-editor`, `add-ai-explanation-panel`, `add-openapi-typescript-codegen`, `add-mermaid-export`.
- **First public demo**: with backend running and Ollama (local or cloud) configured, `npm run dev` opens a browser at `http://localhost:3000` where typing a prompt produces a rendered diagram.
