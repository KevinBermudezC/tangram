## Context

The backend has produced the entire MVP up to the moment of "what does the user see". This proposal is where we cross that line. The constraints:

- Scope must stay tight. If we ship "editor + persistence + codegen + AI panel + landing" all in one PR, review becomes impossible and the next merge takes weeks.
- The frontend toolchain must be boring. Next.js + TypeScript + Tailwind + React Flow is the most common stack in the dev-tool space; sticking to it keeps onboarding low-friction.
- The TypeScript types must match the backend Pydantic schemas exactly. Drift between them is the most expensive bug class we can ship.
- The first version is **read-only**. The user types, the AI generates, the canvas renders. The next proposal adds editing.

## Goals / Non-Goals

**Goals:**

- One Next.js workspace under `frontend/` that runs with `corepack enable && pnpm install && pnpm dev`.
- A single page that lets a user generate and view a diagram.
- React Flow renders the diagram with the auto-layout positions the backend assigned.
- Typed error handling — the backend's `code` field maps to user-readable messages.
- Tests + lint + typecheck running in CI alongside the Python jobs.

**Non-Goals:**

- Editing. Read-only render only.
- Persistence. The diagram lives in component state until the user refreshes.
- Multi-page routing, auth UI, landing page, settings. One page suffices for MVP.
- A design system. Tailwind utility classes get us through MVP; if we need consistent components, add shadcn/ui in a follow-up.
- OpenAPI codegen. Types are hand-written; the codegen proposal replaces them later.
- E2E tests with Playwright. Vitest + Testing Library unit/component tests are enough for v0.

## Decisions

### Next.js 16 with the App Router

Next.js is the default React metaframework, App Router is the current shape, the team behind Tangram has TypeScript experience. This needs no further argument. Originally drafted against Next.js 15; bumped to 16 during implementation to pick up the React 19 + Turbopack defaults. Node.js floor moved with it (16 wants 22+).

**Alternatives considered**: Vite + React Router (rejected — Next.js is more common in this space, smaller leap for contributors), Remix (rejected — losing momentum vs Next.js in 2025), plain React + Vite (rejected — we'll likely want SSR later for sharing diagrams).

### Tailwind CSS

Tailwind v4 is the standard styling layer for new Next.js projects. Component libraries (shadcn/ui, etc.) integrate with it. Skipping it now and adding it later is more work than starting with it.

**Alternatives considered**: CSS Modules (rejected — fine but more verbose), styled-components (rejected — runtime cost, less idiomatic in App Router), no CSS framework (rejected — we're styling something that has to look professional eventually).

### React Flow (`@xyflow/react`) version 12

React Flow is purpose-built for editable node-and-edge graphs. v12 is the current major version with a stable API and React 19 support.

**Alternatives considered**: D3 from scratch (rejected — months of work, we don't need novel layout), Cytoscape.js (rejected — heavier API, less React-native), Reagraph / G6 / Sigma (rejected — community/docs smaller than React Flow's).

### Hand-written TypeScript types matching backend Pydantic schemas

`frontend/types/tangram.ts` declares `Diagram`, `Node`, `Edge`, `NodeType`, etc. by hand. A comment at the top of the file says "this file mirrors `backend/app/schemas/diagram.py`; future codegen will replace it; until then, edits here and there must stay in sync".

**Why**: codegen is real work (`openapi-typescript`, build pipeline, CI step). Doing it as its own proposal lets us focus this PR on the visible result and removes a coupling. For 4-5 types totaling ~80 lines, hand-writing is fine.

**Alternatives considered**: full codegen now (rejected — bloats this PR, see scope-control note in context), Zod schemas matching Pydantic (rejected — adds runtime validation we don't need yet).

### Read-only React Flow canvas

We render nodes via React Flow but disable drag, connect, and edit. The canvas is a viewer in v0.

**Why**: editing is genuinely separate concerns (state management, drag handlers, edge creation UX, validation feedback). Bundling it with foundation makes review awful and ships nothing for a long time.

**Alternatives considered**: full editor in this PR (rejected — too big), static image with a screenshot library (rejected — defeats the point of React Flow).

### One env var: `NEXT_PUBLIC_API_URL`

The frontend needs to know where the backend lives. Defaults to `http://localhost:8000`. Configurable for non-default deployments.

`NEXT_PUBLIC_` prefix is required for client-side env vars in Next.js. The backend's `cors_origins` setting already allows `http://localhost:3000` by default, so the round trip works without further config.

**Alternatives considered**: Next.js rewrites (proxy `/api/*` to backend) (rejected — adds a server hop in dev for negligible benefit), hardcoded URL (rejected — breaks production deploys).

### ESLint via `eslint-config-next`, no separate Prettier

Next.js 16 ships an ESLint preset that covers most of what Prettier would do. Adding Prettier means setting up the ESLint/Prettier compatibility shim, which is one more thing to break. Skip until we feel the pain.

**Alternatives considered**: ESLint + Prettier with `eslint-config-prettier` (rejected — extra config surface), Biome (rejected — appealing but the Next.js community is still mostly on ESLint; contributor familiarity wins), no linter (rejected — obviously not).

### Vitest, not Jest

Vitest is fast, ESM-native, and has first-class Vite/Next.js integration in 2025. Jest works but is slower and has more config friction with TypeScript.

**Alternatives considered**: Jest (rejected — slower setup, more deps), no tests (rejected — we want CI parity with the backend).

### CI integration as a separate job

The existing CI has `lint`, `test`, `openspec` Python jobs. We add a fourth: `frontend`. Runs `pnpm install --frozen-lockfile`, then `pnpm lint`, `pnpm typecheck`, `pnpm test`. Parallel to the others. pnpm is installed via `pnpm/action-setup@v4` before `actions/setup-node@v4` so the `cache: pnpm` feature can resolve the store path.

**Alternatives considered**: extend the existing `lint` and `test` jobs to also run frontend (rejected — mixes Python and Node tooling per job, makes failures harder to read).

## Risks / Trade-offs

- **Risk**: type drift between hand-written TypeScript and backend Pydantic schemas. → **Mitigation**: a comment in `types/tangram.ts` flags it as hand-written; codegen lands in a follow-up. For MVP scope (5 types), the maintenance cost is bounded.
- **Risk**: React Flow's auto-layout disabled means our backend `auto_layout` is responsible for readable diagrams. → **Mitigation**: the backend's column-by-type layout is good enough for 5-10 node diagrams; if real diagrams expose layout failures we add a frontend-side layout layer.
- **Risk**: CORS misconfiguration in development. → **Mitigation**: the backend default `CORS_ORIGINS` already includes `http://localhost:3000`; we document this in both READMEs.
- **Risk**: the React Flow CSS import order can break with Tailwind. → **Mitigation**: import React Flow's stylesheet *before* Tailwind directives in `globals.css` and verify in the smoke test.
- **Trade-off**: this PR is the largest so far in raw line count. We accept it because it's the smallest viable end-to-end frontend; further splitting would leave the user with a broken half-stack on `main`.

## Migration Plan

No migration. New directory.

## Open Questions

- **Should we run the frontend dev server through `concurrently` with the backend?** Convenient but couples two processes. Skip until a contributor asks for it.
- **Should we ship a Dockerfile for the frontend?** Probably yes eventually for production deployments. For dev it adds nothing. Defer to a separate proposal.
- **Do we want a basic landing/marketing page now or later?** Later. The point of this PR is the working tool; the landing page can be its own design exercise.
