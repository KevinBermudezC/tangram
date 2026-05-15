# Tangram frontend

Next.js 15 + React 19 + React Flow. Pre-alpha.

## Prerequisites

- Node.js 20+
- The Tangram backend running (see [`../backend/README.md`](../backend/README.md))

## Quick start

```bash
cd frontend
npm install
cp .env.example .env.local   # optional — defaults to http://localhost:8000
npm run dev
```

Open <http://localhost:3000>. Type a prompt, click Generate, see a diagram.

The page expects the backend at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). The backend's default `CORS_ORIGINS` already allows `http://localhost:3000`, so the round trip works without any further config.

## Project layout

```
frontend/
├── app/
│   ├── layout.tsx        # HTML shell, Tailwind import
│   ├── page.tsx          # The single page (prompt + canvas + error states)
│   └── globals.css       # Tailwind directives
├── components/
│   ├── PromptForm.tsx    # textarea + submit button
│   └── DiagramCanvas.tsx # React Flow wrapper, read-only
├── lib/
│   ├── api.ts            # generate() + TangramApiError
│   └── diagramToFlow.ts  # Tangram Diagram → React Flow {nodes,edges}
├── types/
│   └── tangram.ts        # Hand-written TS mirrors of backend Pydantic schemas
├── tests/                # Vitest suite
├── package.json
├── tsconfig.json         # strict: true
├── eslint.config.mjs
├── vitest.config.ts
└── .env.example
```

## Commands

| Command            | What it does                                  |
| ------------------ | --------------------------------------------- |
| `npm run dev`      | Start dev server with hot reload              |
| `npm run build`    | Production build                              |
| `npm run start`    | Start the built app                           |
| `npm run lint`     | ESLint (Next.js preset)                       |
| `npm run typecheck`| `tsc --noEmit` against the strict config      |
| `npm run test`     | Run the Vitest suite once                     |
| `npm run test:watch`| Vitest in watch mode                         |

## What this version does

- Renders a single page with a prompt textarea and a Generate button.
- On submit, calls `POST /generate` on the backend.
- Surfaces backend errors using the typed `code` field.
- Renders the returned diagram in a **read-only** React Flow canvas (pan + zoom enabled, drag/connect/edit disabled).

## What this version does NOT do (yet)

| Feature                    | Lands in                              |
| -------------------------- | ------------------------------------- |
| Editing the diagram        | `add-diagram-editor`                  |
| Saving / loading diagrams  | `add-diagram-persistence-routes`      |
| Per-node AI explanation    | `add-ai-explanation-panel`            |
| Export to Mermaid          | `add-mermaid-export`                  |
| Auto-generated TS types    | `add-openapi-typescript-codegen`      |

## Types

`types/tangram.ts` is hand-written today. It mirrors `backend/app/schemas/diagram.py` and related schemas. **If you change the backend schema, change this file in the same PR.** The future `add-openapi-typescript-codegen` proposal removes this maintenance step.

## Styling

Tailwind CSS v4 via PostCSS. React Flow's stylesheet is imported in `DiagramCanvas.tsx`.

## Troubleshooting

| Symptom                                         | Likely cause / fix                                            |
| ----------------------------------------------- | ------------------------------------------------------------- |
| `Failed to fetch` in the console                | Backend not running, or `NEXT_PUBLIC_API_URL` is wrong        |
| CORS errors                                     | Backend's `CORS_ORIGINS` doesn't include your frontend origin |
| Diagram renders but nodes are stacked at (0, 0) | Backend's `auto_layout` didn't run (check backend logs)        |
| `code: llm_config_error`                        | Backend's LLM provider keys aren't set; see backend README    |
