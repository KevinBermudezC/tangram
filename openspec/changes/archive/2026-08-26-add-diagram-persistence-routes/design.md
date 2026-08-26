## Context

`POST /generate` produces a complete `Diagram` (it already carries an `id` and `metadata` with `createdAt`/`updatedAt`) but nothing persists it. The `persistence-layer` spec fixes the on-disk contract: one JSON file per diagram at `<DATA_DIR>/diagrams/<id>.json`, serialized with `Diagram.model_dump_json(by_alias=True, indent=2)`, parents auto-created, no relational DB. What's missing is (a) a service that performs those reads/writes and (b) HTTP routes exposing them. This is a backend-only change; the frontend already has a mock `useDiagrams` hook waiting to be pointed at a real `GET /diagrams`.

Relevant existing shapes:
- `Diagram` (`app/schemas/diagram.py`): `version, id, metadata{name, description, createdAt, updatedAt}, nodes, edges, conversation`.
- Typed errors via `TangramHTTPError` → flat `{"detail", "code"}` body (see `app/routers/ai.py`).
- `python-ulid` is installed; ULIDs are lexicographically sortable by creation time.

## Goals / Non-Goals

**Goals:**
- A reusable storage service: `save`, `list`, `get`, `delete`, depending only on the filesystem.
- Four routes (`POST/GET /diagrams`, `GET/DELETE /diagrams/{id}`) with the established typed-error contract.
- Stable, sortable ids (ULID) so "newest first" is a string sort with no extra index.
- Keep the backend bootable with no DB and no new dependency.

**Non-Goals:**
- Modifying `/generate` to auto-save (saving stays an explicit client call).
- The editor, `/analyze`, OpenAPI codegen, auth/multi-user, pagination, search.
- Concurrency control beyond last-write-wins (single-user local app).

## Decisions

**1. New router `app/routers/diagrams.py` + new service, not folded into `ai.py`.**
`ai.py` is for LLM-driven endpoints; persistence is a different concern. A dedicated router keeps the error-mapping for storage (not-found) separate from LLM error-mapping. Registered in `app/main.py` alongside the existing routers.

**2. Storage service is a thin filesystem repository.**
Location: `app/services/storage/` (mirrors the `services/<domain>/` layout already used by `generation`, `retrieval`, etc.). Functions: `save_diagram(d) -> Diagram`, `list_diagrams() -> list[DiagramSummary]`, `get_diagram(id) -> Diagram | None`, `delete_diagram(id) -> bool`. The `DATA_DIR` is read from settings; `<DATA_DIR>/diagrams/` is created on first write. Alternative considered: a class-based repository injected via FastAPI `Depends`. Rejected for now — module-level functions match the existing service style and there's only one implementation.

**3. `POST /diagrams` accepts a full `Diagram`; server owns timestamps and missing ids.**
- If the incoming `id` is empty, assign a new ULID.
- On save, set `metadata.updatedAt = now`. Preserve `metadata.createdAt` if the file already exists; otherwise set it to `now`.
- Return the stored `Diagram` (so the client learns the assigned id/timestamps).
Rationale: the generate→save handoff sends a diagram that already has an id; re-saving an edited diagram must keep `createdAt` stable and bump `updatedAt`. Alternative (accept a separate "create" body without id) was rejected as redundant with the existing `Diagram` schema.

**4. `GET /diagrams` returns lightweight `DiagramSummary`, not full diagrams.**
New schema `DiagramSummary{ id, name, description, createdAt, updatedAt, nodeCount, edgeCount }`. The library list shouldn't ship every node/edge. Summaries are sorted by `id` descending (ULID ⇒ newest first). Reading every file to build summaries is acceptable at MVP scale (tens of diagrams); a manifest/index is a future optimization noted under Risks.

**5. Not-found is a typed 404 with `code: "diagram_not_found"`.**
`GET`/`DELETE` on an unknown id raise `TangramHTTPError(404, code="diagram_not_found")`, matching the frontend's existing pattern of branching on a stable top-level `code`.

**6. Id validation.** Path `{id}` is validated to be a syntactically plausible diagram id (ULID-shaped: 26 Crockford base32 chars) before touching the filesystem, to prevent path traversal (`..`, `/`). Reject malformed ids with `422`/`404` rather than reading arbitrary paths.

## Risks / Trade-offs

- **Listing reads every file on each `GET /diagrams`** → O(n) disk reads. Mitigation: fine for MVP (tens of files); revisit with a `data/diagrams/index.json` manifest if it ever matters. Noted, not built.
- **Last-write-wins, no locking** → two concurrent saves of the same id can clobber. Mitigation: acceptable for a single-user local app; out of scope per Non-Goals.
- **Path traversal via crafted id** → could read/delete arbitrary files. Mitigation: strict id-shape validation before any filesystem access (Decision 6).
- **Corrupt/half-written JSON file** → a list/get could raise. Mitigation: `save` writes to a temp file then atomically renames; `list` skips files that fail to parse and logs a warning rather than failing the whole request.
- **Schema drift** (a stored diagram from an older `version`) → parse may fail. Mitigation: out of scope now; the `version` field exists to support a future migration step.
