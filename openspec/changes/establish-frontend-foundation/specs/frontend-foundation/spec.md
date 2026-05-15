## ADDED Requirements

### Requirement: Next.js workspace under `frontend/`

The repository SHALL include a Next.js 15 + TypeScript workspace at `frontend/`. A contributor with Node.js 20+ installed SHALL be able to run `npm install && npm run dev` and see the application on `http://localhost:3000`.

#### Scenario: Fresh install and run

- **WHEN** a contributor clones a fresh repo, runs `cd frontend && npm install && npm run dev`
- **THEN** the dev server boots without errors
- **AND** `http://localhost:3000` returns 200

#### Scenario: TypeScript strict mode is on

- **WHEN** `npm run typecheck` is run
- **THEN** TypeScript runs with `strict: true` and the project has zero type errors

### Requirement: Prompt → Generate → Render flow

The home page SHALL contain a textarea, a Generate button, and a canvas. When the user submits a prompt, the page SHALL call `POST /generate` on the backend, render the returned diagram in the canvas, and surface loading and error states.

#### Scenario: Happy path renders the diagram

- **WHEN** the user types "I want to build a delivery app" and clicks Generate, and the backend returns a valid Diagram
- **THEN** the loading state is shown while the request is in flight
- **AND** when the response arrives, the canvas renders one React Flow node per `Diagram.nodes` entry and one edge per `Diagram.edges` entry

#### Scenario: Backend error is surfaced

- **WHEN** the backend responds with a non-200 status that contains `{detail, code}`
- **THEN** the page shows a user-readable error message that includes the `code`
- **AND** the canvas is cleared or left empty (does not show a stale diagram)

### Requirement: Read-only canvas in v0

The React Flow canvas SHALL render the diagram but SHALL NOT allow editing in this proposal. Drag, connect, and edit handlers SHALL be disabled. Pan and zoom MAY be enabled (they're read interactions, not edits).

#### Scenario: Dragging a node does nothing

- **WHEN** the user attempts to drag a node on the rendered canvas
- **THEN** the node does not move
- **AND** no edit event is fired

#### Scenario: Pan and zoom remain usable

- **WHEN** the user pans or zooms the canvas
- **THEN** the view updates normally

### Requirement: TypeScript types mirror backend Pydantic schemas

`frontend/types/tangram.ts` SHALL declare TypeScript types that mirror the shape of the backend Pydantic schemas (`Diagram`, `Node`, `Edge`, `NodeType`, `DataFlow`, `Message`, and related). These types SHALL be hand-written for this proposal; a future proposal replaces them with auto-generated equivalents.

#### Scenario: Hand-written types compile cleanly

- **WHEN** the frontend is type-checked
- **THEN** the types in `types/tangram.ts` are referenced by the API client and the diagram adapter without errors

#### Scenario: Type file is marked as temporary

- **WHEN** a contributor opens `types/tangram.ts`
- **THEN** a header comment notes that this file is hand-written and will be replaced by codegen in a future proposal

### Requirement: API client error shape matches backend

`frontend/lib/api.ts` SHALL expose a typed `generate(prompt)` function. On non-2xx responses, it SHALL throw a typed error that exposes the backend's `detail` string and `code` string at the top level.

#### Scenario: Successful generate returns a Diagram

- **WHEN** the backend responds 200 with a valid Diagram body
- **THEN** the client returns a parsed `Diagram` value

#### Scenario: Failure throws a TangramApiError

- **WHEN** the backend responds with `{detail, code}` and a non-2xx status
- **THEN** the client throws an error instance exposing `code` as a top-level string

### Requirement: Diagram-to-flow adapter

A function `diagramToFlow(diagram)` in `frontend/lib/` SHALL convert a Tangram `Diagram` into the React Flow `{ nodes, edges }` shape. Position from the backend SHALL be preserved. Node labels SHALL come from `Node.label`.

#### Scenario: Each diagram node becomes a React Flow node

- **WHEN** a Diagram with 3 nodes is adapted
- **THEN** the result `.nodes` has length 3
- **AND** each adapted node has `id`, `position`, and a `data.label` matching the original

#### Scenario: Each diagram edge becomes a React Flow edge

- **WHEN** a Diagram with 2 edges is adapted
- **THEN** the result `.edges` has length 2
- **AND** each adapted edge has `source` and `target` matching the original edge

### Requirement: Configurable backend URL

The frontend SHALL read the backend URL from `NEXT_PUBLIC_API_URL` with a default of `http://localhost:8000`. Production deployments SHALL be configurable by setting this variable at build time.

#### Scenario: Default URL works in dev

- **WHEN** `NEXT_PUBLIC_API_URL` is unset
- **THEN** the API client targets `http://localhost:8000`

#### Scenario: Override URL is honored

- **WHEN** `NEXT_PUBLIC_API_URL=https://api.example.com` is set at build time
- **THEN** the built app's API client targets that URL
