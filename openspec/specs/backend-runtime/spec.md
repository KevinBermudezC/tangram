# backend-runtime Specification

## Purpose
TBD - created by archiving change establish-mvp-foundations. Update Purpose after archive.
## Requirements
### Requirement: HTTP runtime

The backend SHALL expose an HTTP service implemented with FastAPI, running on port 8000 by default.

#### Scenario: Backend boots and responds to health probe

- **WHEN** the backend container starts and `GET /health` is requested
- **THEN** the response status is 200 and the body includes `status: "ok"`, `name`, `version`, and `environment` fields

#### Scenario: Health check exposes runtime metadata

- **WHEN** `GET /health` is requested
- **THEN** the response body includes the configured application name and the running version

### Requirement: Configuration surface

The backend SHALL load configuration from environment variables using Pydantic Settings, with sane defaults for local development.

#### Scenario: Defaults work without an .env file

- **WHEN** the backend starts with no `.env` file present and no environment variables set
- **THEN** the backend boots successfully and serves `/health` using the default values

#### Scenario: Environment variables override defaults

- **WHEN** `DATABASE_URL` is set in the environment to a non-default value
- **THEN** the running settings reflect the override

#### Scenario: Unknown environment variables are ignored

- **WHEN** an unrelated environment variable is present
- **THEN** the backend boots without raising

### Requirement: CORS allowlist

The backend SHALL apply a CORS middleware that allows the configured frontend origin and rejects others by default.

#### Scenario: Frontend origin is allowed

- **WHEN** a request originates from `http://localhost:3000` (the default)
- **THEN** the response includes the CORS headers permitting the origin

#### Scenario: Unconfigured origin is rejected

- **WHEN** a request originates from an origin not in `CORS_ORIGINS`
- **THEN** the browser will block the response per CORS rules

### Requirement: Project layout conventions

The backend SHALL organize code under `app/{core,middlewares,routers,schemas,tables,services}` to give all future code a predictable home.

#### Scenario: Pydantic schema imports

- **WHEN** another module imports `from app.schemas.diagram import Diagram`
- **THEN** the import resolves to the canonical Pydantic model that mirrors the diagram schema

#### Scenario: Router registration

- **WHEN** a new router file is added under `app/routers/`
- **THEN** it can be wired into the FastAPI app by including it in `app/main.py` without other layout changes

### Requirement: Diagram schema parity with documentation

The Pydantic schema in `app/schemas/diagram.py` SHALL match the canonical diagram schema described in `docs/schema/diagram-v0.md`, including all node types, data flow values, and field names with their `camelCase` JSON aliases.

#### Scenario: Round-trip from JSON example

- **WHEN** the example JSON document from `docs/schema/diagram-v0.md` is parsed via `Diagram.model_validate`
- **THEN** the parse succeeds and `Diagram.model_dump(by_alias=True)` yields the original document modulo whitespace

#### Scenario: Closed enum on node type

- **WHEN** a JSON document includes a node with an unrecognized `type` value
- **THEN** the parse raises a validation error rather than accepting the unknown type

