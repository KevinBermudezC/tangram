## Why

The persistence HTTP API (`POST/GET/DELETE /diagrams`) and the live hooks (`useDiagrams`, `useDiagram`, `useSaveDiagram`) already exist on `main`, but Library and the rail Recent list still type their view model as `MockDiagram` from `frontend/lib/mock-data.ts`. When the backend is down or the store is empty, those surfaces collapse to an empty list and read as "no diagrams" rather than an error — the opposite of a real generate → save → library → reopen loop. Issue #18 and `ROADMAP.md` still describe this work as unstarted.

## What Changes

- Replace `MockDiagram` as the live list view model with a UI type that is not named or imported from `mock-data.ts`. Cards, thumbs, Library, and the rail keep working.
- Keep `mock-data.ts` as the static catalog for templates and the palette only — not saved-diagram records.
- Show distinct loading / empty / error states on Library and Recent when `GET /diagrams` is in flight, returns `[]`, or fails (backend down). No fake recent diagrams.
- Add tests for the list mapper/hooks and the Library (and rail, where practical) empty/error states.
- Update `ROADMAP.md` so item #13 and the Library/Recent follow-up match reality.
- Archive the completed backend change `add-diagram-persistence-routes` (all of its tasks are done; frontend was explicitly a follow-up).

Non-goals: chat-about-diagram, Mermaid export, dark mode, restyling node colors, adding `PATCH /diagrams` (upsert remains `POST /diagrams`), and wiring the disabled card Delete menu (the API client already has `deleteDiagram`).

## Capabilities

### New Capabilities
- `frontend-diagram-persistence`: Library, Recent, and `/editor/[id]` consume the live `/diagrams` API. Saved-diagram list items use a real view model (not `MockDiagram`). Empty and error states are honest when the store is empty or the backend is unreachable.

### Modified Capabilities
<!-- None. Persistence routes, the diagram schema, and the editor autosave contract are reused unchanged. -->

## Impact

- **Code:** `frontend/lib/hooks.ts`, a small list view-model module, `diagram-card.tsx` / `diagram-thumb.tsx`, Library page, `app-rail.tsx`, tests. Docs: `ROADMAP.md`, `frontend/README.md`.
- **OpenSpec:** new change here; archive `openspec/changes/add-diagram-persistence-routes` into `openspec/specs/diagram-persistence-routes` + `openspec/changes/archive/`.
- **APIs / dependencies:** none new. Reuses existing `listDiagrams` / `getDiagram` / `saveDiagram`.
- **Issue:** GitHub #18. Close it if the generate → save → library → `/editor/{ulid}` loop is actually done (PATCH was never in the backend design; POST upserts).
