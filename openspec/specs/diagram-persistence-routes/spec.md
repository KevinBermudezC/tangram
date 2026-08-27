# diagram-persistence-routes Specification

## Purpose

Filesystem-backed HTTP API for persisting, listing, fetching, and deleting diagrams as JSON files under `<DATA_DIR>/diagrams/`, without a relational database.

## Requirements

### Requirement: Diagram storage service

The backend SHALL provide a storage service that persists, lists, fetches, and deletes diagrams using the filesystem layout defined by the `persistence-layer` capability (`<DATA_DIR>/diagrams/<id>.json`). The service SHALL NOT require a relational database.

#### Scenario: Save creates the diagrams directory

- **WHEN** a diagram is saved and `<DATA_DIR>/diagrams/` does not yet exist
- **THEN** the directory and any missing parents are created
- **AND** the diagram is written to `<DATA_DIR>/diagrams/<id>.json` using `Diagram.model_dump_json(by_alias=True, indent=2)`

#### Scenario: Save is atomic

- **WHEN** a diagram is written to disk
- **THEN** the content is written to a temporary file and atomically renamed into place
- **AND** a reader never observes a partially written file

#### Scenario: List skips unreadable files

- **WHEN** the diagrams directory contains a file that is not valid diagram JSON
- **THEN** listing logs a warning and omits that file
- **AND** the remaining valid diagrams are still returned

### Requirement: Persist a diagram

The backend SHALL expose `POST /diagrams` that accepts a `Diagram` body, persists it, and returns the stored `Diagram`. The server SHALL own identity and timestamps: if the incoming `id` is empty it SHALL assign a new ULID; on every save it SHALL set `metadata.updatedAt` to the current time; it SHALL set `metadata.createdAt` to the current time only when no file for that id already exists, otherwise preserving the existing `createdAt`.

#### Scenario: Persist a new diagram without an id

- **WHEN** a client sends `POST /diagrams` with an empty `id`
- **THEN** the server assigns a new ULID as the `id`
- **AND** sets `metadata.createdAt` and `metadata.updatedAt` to the current time
- **AND** responds `201` with the stored diagram including the assigned `id`

#### Scenario: Re-saving an existing diagram preserves createdAt

- **WHEN** a client sends `POST /diagrams` with an `id` that already has a stored file
- **THEN** the stored `metadata.createdAt` is preserved
- **AND** `metadata.updatedAt` is set to the current time
- **AND** the file at `<DATA_DIR>/diagrams/<id>.json` is overwritten with the new content

### Requirement: List diagram summaries

The backend SHALL expose `GET /diagrams` that returns a list of lightweight summaries — `id`, `name`, `description`, `createdAt`, `updatedAt`, `nodeCount`, `edgeCount`, and a geometry-only `thumb` — and SHALL NOT return full node and edge data (labels, properties, AI annotations). Summaries SHALL be ordered by `id` descending so that the most recently created diagrams (ULID-sortable) appear first.

The `thumb` SHALL be a downscaled projection of the diagram into a fixed 200×120 coordinate space: a list of node rects (`type`, `x`, `y`, `w`, `h`) and a list of edge lines (`from`/`to` points at node-rect centers, plus a `dashed` flag). It SHALL carry no node labels, properties, or AI annotations, so it remains lightweight while letting the frontend render an SVG preview without fetching every full diagram.

#### Scenario: Empty store

- **WHEN** `GET /diagrams` is called and no diagrams exist
- **THEN** the response is `200` with an empty array

#### Scenario: Summaries are newest-first and lightweight

- **WHEN** `GET /diagrams` is called and several diagrams exist
- **THEN** each item contains `id`, `name`, `description`, `createdAt`, `updatedAt`, `nodeCount`, `edgeCount`, `thumb`
- **AND** the items are ordered by `id` descending
- **AND** no item includes the full `nodes` or `edges` arrays

#### Scenario: Thumb is a bounded geometry-only projection

- **WHEN** a summary's `thumb` is produced for a diagram with one or more nodes
- **THEN** each thumb node rect lies fully within the 200×120 viewBox
- **AND** each thumb node carries only `type` and geometry (`x`, `y`, `w`, `h`), never a label or properties

### Requirement: Fetch a diagram by id

The backend SHALL expose `GET /diagrams/{id}` that returns the full stored `Diagram` for a known id, and a typed `404` with `code: "diagram_not_found"` for an unknown id.

#### Scenario: Fetch an existing diagram

- **WHEN** `GET /diagrams/{id}` is called for a stored diagram
- **THEN** the response is `200` with the full `Diagram` body

#### Scenario: Fetch a missing diagram

- **WHEN** `GET /diagrams/{id}` is called for an id with no stored file
- **THEN** the response is `404` with body `{"detail": ..., "code": "diagram_not_found"}`

### Requirement: Delete a diagram

The backend SHALL expose `DELETE /diagrams/{id}` that removes the stored file for a known id and returns a typed `404` with `code: "diagram_not_found"` for an unknown id.

#### Scenario: Delete an existing diagram

- **WHEN** `DELETE /diagrams/{id}` is called for a stored diagram
- **THEN** the file at `<DATA_DIR>/diagrams/<id>.json` is removed
- **AND** the response is `204` with no body
- **AND** a subsequent `GET /diagrams/{id}` returns `404`

#### Scenario: Delete a missing diagram

- **WHEN** `DELETE /diagrams/{id}` is called for an id with no stored file
- **THEN** the response is `404` with body `{"detail": ..., "code": "diagram_not_found"}`

### Requirement: Diagram id path validation

The backend SHALL validate the `{id}` path parameter against the ULID shape (26 Crockford base32 characters) before performing any filesystem access, rejecting malformed ids so that path-traversal sequences cannot reach the filesystem.

#### Scenario: Reject a path-traversal id

- **WHEN** a request targets `GET /diagrams/{id}` with an `id` that is not a valid ULID (for example one containing `/` or `..`)
- **THEN** the server rejects the request before any filesystem access
- **AND** responds with `422` or `404` and never reads a path outside `<DATA_DIR>/diagrams/`
