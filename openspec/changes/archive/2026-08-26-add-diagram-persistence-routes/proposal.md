## Why

Today `POST /generate` returns a `Diagram` and immediately discards it — nothing is written to disk, and there is no way to list or re-open a diagram. As a result the entire frontend (Library, Recent, and the future `/editor/[id]` route) runs on mock data. The accepted `persistence-layer` spec already defines *where* a diagram lives on disk (`<DATA_DIR>/diagrams/<id>.json`), but no service writes there and no HTTP routes expose it. This change closes the core MVP loop: **generate → save → see it in the library → re-open it.**

## What Changes

- Add a filesystem-backed **diagram storage service** in the backend that can save, list, fetch-by-id, and delete diagrams, honoring the existing `persistence-layer` filesystem contract (`<DATA_DIR>/diagrams/<id>.json`, written via `Diagram.model_dump_json(by_alias=True, indent=2)`, parent dirs auto-created, no relational DB).
- Add **REST routes** for diagram persistence:
  - `POST /diagrams` — persist a diagram (assigns a ULID if absent), returns the stored diagram.
  - `GET /diagrams` — list lightweight summaries (id, title, timestamps) for the library, newest first.
  - `GET /diagrams/{id}` — fetch a full diagram by id (`404` if missing).
  - `DELETE /diagrams/{id}` — remove a diagram (`404` if missing).
- Reuse the existing `TangramHTTPError` typed-error contract (flat `{"detail", "code"}` body) established in `app/routers/ai.py`, adding a `diagram_not_found` code.
- Diagram ids are **ULIDs** (lexicographically sortable, so "newest first" needs no extra timestamp index). `python-ulid` is already a dependency.

Non-goals (explicitly out of scope for this change): the diagram editor / drag-drop, the `POST /analyze` endpoint, OpenAPI→TypeScript codegen, and any multi-user / auth concerns. `POST /generate` is **not** modified to auto-persist; saving stays an explicit client action so generation and storage remain decoupled.

The motivating consumer is the frontend: once these routes exist, `lib/hooks.ts:useDiagrams` swaps its mock body for `GET /diagrams`, and the `/editor/[id]` route loads via `GET /diagrams/{id}`. That frontend wiring is a **follow-up** change, not part of this one.

## Capabilities

### New Capabilities
- `diagram-persistence-routes`: the HTTP API for persisting, listing, fetching, and deleting diagrams, plus the storage service backing it.

### Modified Capabilities
<!-- None. The filesystem layout, embedder, and "no relational DB" requirements
     in persistence-layer are reused unchanged; this change implements against
     them rather than altering them. -->

## Impact

- **New code:** a storage service module under `backend/app/services/` (save/list/get/delete), and a new router (e.g. `backend/app/routers/diagrams.py`) registered in `app/main.py`.
- **New schema:** a `DiagramSummary` model for the list endpoint (id, title, created/updated timestamps).
- **APIs:** four new routes under `/diagrams`. No change to `/health` or `/generate`.
- **Dependencies:** none new (`python-ulid` already installed).
- **Storage:** writes appear under `<DATA_DIR>/diagrams/` (default `data/diagrams/`), already git-ignored.
- **Downstream (follow-up, not here):** frontend `useDiagrams` and `/editor/[id]` wiring; a future `add-diagram-editor` save button calls `POST /diagrams`.
