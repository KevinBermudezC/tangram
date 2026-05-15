## 1. Scaffold the Next.js workspace

- [x] 1.1 Add `frontend/package.json` with Next.js 16, React 19, React Flow (`@xyflow/react`), Tailwind v4, Vitest, Testing Library, ESLint 9 (flat config)
- [x] 1.2 Add `frontend/tsconfig.json` with `strict: true`
- [x] 1.3 Add `frontend/next.config.mjs`, `frontend/postcss.config.mjs`, `frontend/eslint.config.mjs`
- [x] 1.4 Add `frontend/.gitignore` (node_modules, .next, etc.)
- [x] 1.5 Add `frontend/.env.example` documenting `NEXT_PUBLIC_API_URL`

## 2. App shell

- [x] 2.1 Add `frontend/app/layout.tsx` — HTML shell, imports Tailwind
- [x] 2.2 Add `frontend/app/globals.css` with Tailwind v4 directive
- [x] 2.3 Add `frontend/app/page.tsx` — the prompt + canvas page

## 3. Types and API client

- [x] 3.1 Add `frontend/types/tangram.ts` mirroring the Pydantic schemas. Header comment notes hand-written status.
- [x] 3.2 Add `frontend/lib/api.ts` with typed `generate(prompt)` and `TangramApiError` class

## 4. Diagram-to-flow adapter

- [x] 4.1 Add `frontend/lib/diagramToFlow.ts` converting Diagram to `{ nodes, edges }` for React Flow
- [x] 4.2 Preserve backend-assigned positions
- [x] 4.3 Map node label to React Flow `data.label`

## 5. Components

- [x] 5.1 Add `frontend/components/PromptForm.tsx` — textarea + submit button + loading state
- [x] 5.2 Add `frontend/components/DiagramCanvas.tsx` — React Flow wrapper, read-only (drag/connect disabled)
- [x] 5.3 Wire components into `app/page.tsx` with state for prompt / loading / result / error

## 6. Tests

- [x] 6.1 Add `frontend/vitest.config.ts` with jsdom environment
- [x] 6.2 Add `frontend/tests/setup.ts`
- [x] 6.3 Add `frontend/tests/diagramToFlow.test.ts` — adapter unit test
- [x] 6.4 Add `frontend/tests/api.test.ts` — generate() happy path + error mapping + 422 normalization
- [x] 6.5 Add `frontend/tests/PromptForm.test.tsx` — renders + disabled-when-empty + submits trimmed + loading state

## 7. CI integration

- [x] 7.1 Update `.github/workflows/ci.yml` to add a `frontend` job that runs npm ci, lint, typecheck, test
- [x] 7.2 Verify the job is independent of the Python jobs (parallel execution)

## 8. Documentation

- [x] 8.1 Add `frontend/README.md` documenting setup, commands, env var, and the manual test path
- [x] 8.2 Update top-level `README.md` Quick start section to include the frontend
- [x] 8.3 Update `CONTRIBUTING.md` "Code conventions" to mention frontend tooling

## 9. Verification

- [x] 9.1 `npm run lint` clean in `frontend/`
- [x] 9.2 `npm run typecheck` clean in `frontend/`
- [x] 9.3 `npm run test` clean in `frontend/` (11/11)
- [x] 9.4 Existing 139 backend tests still pass
- [x] 9.5 `openspec validate establish-frontend-foundation --strict`
