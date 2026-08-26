## Purpose

Lets someone generate a diagram, persist it, see it in Library and Recent from the live list API, and reopen it by id — with honest empty and error states instead of mock records.

## ADDED Requirements

### Requirement: Saved-diagram lists come from the persistence API

Library and the rail Recent list SHALL display diagrams returned by `GET /diagrams`. They SHALL NOT read saved-diagram records from static mock data.

#### Scenario: Library shows persisted diagrams

- **WHEN** `GET /diagrams` returns one or more summaries
- **THEN** Library renders a card (or list row) for each summary
- **AND** each item links to `/editor/{id}` using that summary's id

#### Scenario: Recent shows persisted diagrams

- **WHEN** `GET /diagrams` returns one or more summaries
- **THEN** the rail Recent list shows those diagrams (newest first, capped)
- **AND** each item links to `/editor/{id}` using that summary's id

#### Scenario: Empty store is honest

- **WHEN** `GET /diagrams` succeeds with an empty array
- **THEN** Library and Recent show an empty state
- **AND** they do not render placeholder or fake diagram records

### Requirement: List load failure is distinct from empty

When `GET /diagrams` fails (network error or non-2xx), Library and Recent SHALL show an error state that is visually and textually distinct from the empty-store state.

#### Scenario: Backend unreachable

- **WHEN** `GET /diagrams` fails because the backend is down or returns an error
- **THEN** Library shows an error message that the diagrams could not be loaded
- **AND** Recent does not present the failure as "no diagrams yet"

### Requirement: Reopen a saved diagram by id

Opening `/editor/{id}` SHALL load the full diagram via `GET /diagrams/{id}` and render it in the editor canvas when the fetch succeeds.

#### Scenario: Known id loads

- **WHEN** the user opens `/editor/{id}` for a stored diagram
- **THEN** the page fetches `GET /diagrams/{id}`
- **AND** the returned diagram is shown on the canvas

#### Scenario: Missing id is a not-found state

- **WHEN** `GET /diagrams/{id}` returns a typed 404
- **THEN** the editor shows a not-found state with a way back to the library
- **AND** it does not render a mock diagram in place of the missing one

### Requirement: Generate then save is a real persist

After a successful `POST /generate`, the client SHALL persist the returned diagram with `POST /diagrams` so it appears in subsequent `GET /diagrams` results.

#### Scenario: Generated diagram is saved

- **WHEN** generation succeeds
- **THEN** the client sends `POST /diagrams` with that diagram
- **AND** a later `GET /diagrams` includes it so Library and Recent can list it
