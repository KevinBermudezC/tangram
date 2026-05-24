## 1. Schemas

- [x] 1.1 Add a `DiagramSummary` Pydantic model (`app/schemas/diagram.py` or a new `app/schemas/diagram_summary.py`) with `id, name, description, createdAt, updatedAt, nodeCount, edgeCount`, using camelCase aliases consistent with `DiagramMetadata`.
- [x] 1.2 Build a helper that derives a `DiagramSummary` from a `Diagram` (maps `metadata.name/description/createdAt/updatedAt`, counts nodes/edges).

## 2. Storage service

- [x] 2.1 Create `app/services/storage/` package (`__init__.py` re-exporting the public functions).
- [x] 2.2 Implement `save_diagram(diagram) -> Diagram`: assign a ULID if `id` is empty, set `updatedAt=now`, set `createdAt=now` only when no file exists (else preserve), write atomically (temp file + `os.replace`) to `<DATA_DIR>/diagrams/<id>.json` via `model_dump_json(by_alias=True, indent=2)`, creating parents.
- [x] 2.3 Implement `get_diagram(id) -> Diagram | None` (returns `None` when the file is missing).
- [x] 2.4 Implement `list_diagrams() -> list[DiagramSummary]`: read each file, skip+warn on parse failures, sort by `id` descending.
- [x] 2.5 Implement `delete_diagram(id) -> bool` (returns `False` when the file is missing).
- [x] 2.6 Add an id-validation helper (ULID shape: 26 Crockford base32 chars) used before any filesystem access; reject ids containing path separators or `..`.

## 3. Routes

- [x] 3.1 Create `app/routers/diagrams.py` with `APIRouter(tags=["diagrams"])` and reuse the `ErrorBody`/`TangramHTTPError` pattern from `app/routers/ai.py`.
- [x] 3.2 `POST /diagrams` → `save_diagram`, return `201` with the stored `Diagram`.
- [x] 3.3 `GET /diagrams` → `list_diagrams`, return `200` with `list[DiagramSummary]`.
- [x] 3.4 `GET /diagrams/{id}` → `get_diagram`, return the `Diagram` or raise `404` with `code="diagram_not_found"`; validate id shape first.
- [x] 3.5 `DELETE /diagrams/{id}` → `delete_diagram`, return `204` or raise `404` with `code="diagram_not_found"`; validate id shape first.
- [x] 3.6 Register the new router in `app/main.py` and document the new `diagram_not_found` error code in the `responses=` metadata.

## 4. Tests

- [x] 4.1 Storage unit tests (use a `tmp_path` `DATA_DIR`): save→get round-trip, ULID assignment on empty id, `createdAt` preserved + `updatedAt` bumped on re-save, list ordering newest-first, list skips corrupt file, delete returns False on missing.
- [x] 4.2 Route tests with FastAPI `TestClient`: `POST` then `GET` list/by-id, `404` shape (`{"detail","code"}`) for unknown id on GET and DELETE, `DELETE` then `GET` returns 404, malformed/path-traversal id rejected before filesystem access.
- [x] 4.3 Confirm summaries omit `nodes`/`edges` and include the count fields.

## 5. Verify & document

- [x] 5.1 Run `ruff format` + `ruff check` + `pytest` from `backend/`; all green.
- [x] 5.2 Manual smoke: `POST /diagrams` with a generated diagram, confirm a file appears under `data/diagrams/`, `GET /diagrams` lists it, `GET /diagrams/{id}` returns it, `DELETE` removes it.
- [x] 5.3 Update `ROADMAP.md` row #13 status and note the frontend wiring (`useDiagrams`, `/editor/[id]`) remains a follow-up.
