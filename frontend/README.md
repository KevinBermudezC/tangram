# Tangram frontend

Next.js + React + React Flow + shadcn-style UI. Pre-alpha.

## Prerequisites

- Node.js 22+ (matches CI; declared as `engines.node` in `package.json`)
- **pnpm** as the package manager (auto-provisioned via Corepack)
- The Tangram backend running (see [`../backend/README.md`](../backend/README.md))

## Quick start

```bash
# One-time: let Node manage pnpm versions via Corepack
corepack enable

cd frontend
pnpm install
cp .env.example .env.local   # optional — defaults to http://localhost:8000
pnpm dev
```

Open <http://localhost:3000>. You land on the **Home** — type a prompt and hit Generate. The backend at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) returns a diagram and the Editor opens with it rendered.

A small `Backend up / offline` pill in the bottom of the left rail tells you whether `uvicorn` is reachable. The backend's default `CORS_ORIGINS` already allows `http://localhost:3000`, so the round trip works without any further config.

> The exact pnpm version is pinned via the `packageManager` field in `package.json`. Corepack reads that and uses the matching version, so contributors don't need to install pnpm globally or worry about version drift.

## Routes

| Route                | What it is                                                                 |
| -------------------- | -------------------------------------------------------------------------- |
| `/`                  | Home. Big centered prompt, v0-style. Sends `?prompt=…` to `/editor`.       |
| `/library`           | Saved diagrams grid + filters + templates. Mock data today.                |
| `/editor`            | Three-column workspace: palette / canvas / AI chat panel.                  |
| `/templates`         | Curated starting points. Placeholder.                                      |
| `/settings`          | Provider keys + theme. Placeholder ("read from `.env` for now").           |
| `/api/chat`          | Passthrough to FastAPI `POST /chat` (tutor + inspect tools).               |

## Project layout

```
frontend/
├── app/
│   ├── (app)/             # Pages that use the rail layout
│   │   ├── layout.tsx     #   AppRail + main area
│   │   ├── page.tsx       #   Home (v0-style prompt)
│   │   ├── library/       #   Library grid + filters
│   │   ├── templates/     #   Curated templates (placeholder)
│   │   └── settings/      #   Settings (placeholder)
│   ├── editor/
│   │   └── page.tsx       # Editor (full-width, no rail)
│   ├── api/
│   │   └── chat/
│   │       └── route.ts   # Passthrough to FastAPI POST /chat
│   ├── layout.tsx         # Root layout (providers, fonts, body)
│   └── globals.css        # Tailwind v4 + @theme tokens
├── components/
│   ├── ui/                # shadcn-style primitives (button, input, card, …)
│   ├── editor/            # Editor-specific: palette, topbar, canvas, chat
│   ├── app-rail.tsx       # Left rail (nav + recents + backend status)
│   ├── backend-status.tsx # /health pill in the rail
│   ├── brand.tsx          # Tangram logotype
│   ├── diagram-card.tsx   # Library card with thumbnail
│   ├── diagram-thumb.tsx  # Hand-rolled SVG mini-thumbnail
│   ├── node-icon.tsx      # Per-node-type icon (Frontend, Backend, …)
│   ├── providers.tsx      # QueryClient + Toaster + Devtools
│   ├── DiagramCanvas.tsx  # Read-only React Flow canvas
│   └── PromptForm.tsx     # Legacy single-page prompt (kept for tests)
├── lib/
│   ├── api.ts             # fetch() against /generate, /health, /diagrams, /analyze
│   ├── chat-request.ts    # live diagram + selected_node_id for /api/chat
│   ├── chat-tool-chip.ts  # inspect_* chip labels for the rail
│   ├── hooks.ts           # useGenerate, useHealth, useDiagrams, useDiagram, useSaveDiagram
│   ├── diagram-list.ts    # Card/rail view model mapped from GET /diagrams summaries
│   ├── diagramToFlow.ts   # Tangram Diagram → React Flow {nodes,edges}
│   ├── mock-data.ts       # Static templates + component catalog (not saved diagrams)
│   ├── node-style.ts      # Per-category fills + strokes + label
│   └── utils.ts           # cn() class merger (clsx + tailwind-merge)
├── types/
│   └── tangram.ts         # Hand-written TS mirrors of backend Pydantic schemas
├── prototype/             # Throwaway HTML/CSS prototype (kept as reference)
├── tests/                 # Vitest suite
├── package.json
├── tsconfig.json
├── eslint.config.mjs
├── vitest.config.ts
└── .env.example
```

## Stack notes

**Styling.** Tailwind CSS v4 via PostCSS, with the Tangram design tokens declared in `app/globals.css` under `@theme`. Utilities (`bg-page`, `text-ink-strong`, `bg-cat-frontend`, etc.) reference `var(--color-*)` so `.dark` can override them. Per-node-type colors live in `lib/node-style.ts`.

**UI primitives.** A lean shadcn-style set in `components/ui/` (Button with CVA variants, Input, Textarea, Card, Badge, Separator, DropdownMenu). Built on Radix where state matters. No `shadcn` CLI was used — the surface is small and the build step stays simple.

**Data layer.** Every backend call goes through TanStack Query hooks in `lib/hooks.ts`. Components consume `useGenerate()` / `useHealth()` / `useDiagrams()` and stay declarative. Caching, retries, and devtools are centralized.

**Chat panel.** Uses `@ai-sdk/react`'s `useChat()` against `/api/chat`. That route is a Next.js passthrough: it maps UIMessages and forwards the live canvas snapshot plus `selected_node_id` to FastAPI `POST /chat`. Inference (tutor mode, retrieval, `inspect_diagram` / `inspect_node`) stays on the backend. Streamdown still renders assistant Markdown; finished `inspect_node` parts may show a short chip (`miró Queue · Orders`). Analyze is the existing rail button, not a chat tool.

**Toasts.** `sonner`, mounted in `components/providers.tsx`. Used for transient feedback ("Diagram generated", "Generation failed"). Blocking errors still render inline.

## Commands

| Command           | What it does                                  |
| ----------------- | --------------------------------------------- |
| `pnpm dev`        | Start dev server with hot reload              |
| `pnpm build`      | Production build                              |
| `pnpm start`      | Start the built app                           |
| `pnpm lint`       | ESLint flat config                            |
| `pnpm typecheck`  | `tsc --noEmit` against the strict config      |
| `pnpm test`       | Run the Vitest suite once                     |
| `pnpm test:watch` | Vitest in watch mode                          |

## What works today

- Home → editor handoff: prompt typed on `/` is sent through to `/editor?prompt=…` and `POST /generate` fires.
- **Editable React Flow canvas**: drag a component from the palette to create a node, move it, connect nodes handle-to-handle, double-click to rename, Delete to remove. Edits serialize back to the `Diagram` schema and autosave (debounced) via `POST /diagrams`; an explicit **Save** button flushes immediately.
- Loading / error / blank states on the editor.
- Library + Recent (mock data, real hooks).
- AI chat panel: select a node, ask why it is there; the tutor inspects that node (not canned keyword replies).
- `/health` polling drives a backend status pill in the rail.

## What's NOT wired yet

| Feature                          | Tracked in                                                |
| -------------------------------- | --------------------------------------------------------- |
| Undo / redo on the canvas        | `add-diagram-editor` follow-up                            |
| Export to Mermaid                | `add-mermaid-export`                                      |
| Per-node AI explanation panel    | `add-ai-explanation-panel`                                |
| Auto-generated TS types          | `add-openapi-typescript-codegen`                          |
| Dark mode                        | Roadmap → Phase 2 → "Dark / light theme"                  |

See [ROADMAP.md](../ROADMAP.md) "Frontend follow-ups" + "Good first issues" for the full list.

## Types

`types/tangram.ts` is hand-written today. It mirrors `backend/app/schemas/diagram.py` and related schemas. **If you change the backend schema, change this file in the same PR.** The future `add-openapi-typescript-codegen` proposal removes this maintenance step.

## Visual prototype

`frontend/prototype/` holds the static HTML/CSS prototype that the Next.js port was built from. It's throwaway — open `index.html` in a browser to see how a state was meant to look, then translate to JSX. Delete the folder whenever it stops being useful as a reference.

## Troubleshooting

| Symptom                                          | Likely cause / fix                                            |
| ------------------------------------------------ | ------------------------------------------------------------- |
| `Failed to fetch` in the console                 | Backend not running, or `NEXT_PUBLIC_API_URL` is wrong        |
| Backend pill in the rail says "offline"          | Same — `uvicorn` not running, or unreachable                  |
| CORS errors                                      | Backend's `CORS_ORIGINS` doesn't include your frontend origin |
| Diagram renders but nodes are stacked at (0, 0)  | Backend's `auto_layout` didn't run (check backend logs)        |
| `code: llm_config_error`                         | Backend's LLM provider keys aren't set; see backend README    |
| `code: llm_input_too_large`                      | Bump `MAX_LLM_INPUT_CHARS` in `backend/.env` (default 64k)    |
