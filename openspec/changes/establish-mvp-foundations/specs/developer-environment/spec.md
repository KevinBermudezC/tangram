## ADDED Requirements

### Requirement: One-command local startup

A contributor with Docker installed SHALL be able to clone the repository and start a working backend with a single command.

#### Scenario: Fresh clone bootstraps successfully

- **WHEN** a contributor runs `docker compose up` from the repository root after a fresh clone
- **THEN** Postgres and the backend service start without manual configuration steps
- **AND** `GET http://localhost:8000/health` returns 200

#### Scenario: Restart preserves database state

- **WHEN** the contributor stops the stack and runs `docker compose up` again
- **THEN** Postgres data persists across the restart through a named Docker volume

### Requirement: Postgres with pgvector extension

The development database SHALL be Postgres 16 with the `pgvector` extension available, regardless of whether any code currently uses vector queries.

#### Scenario: pgvector extension is creatable

- **WHEN** a SQL session connects to the development database and runs `CREATE EXTENSION IF NOT EXISTS vector`
- **THEN** the extension installs successfully without further setup

### Requirement: Configuration documented via `.env.example`

Every configurable surface in the backend SHALL be present in `backend/.env.example` with a placeholder or sensible default.

#### Scenario: New setting added without doc update fails review

- **WHEN** a pull request introduces a new field on `Settings` and does not update `.env.example`
- **THEN** review feedback flags the omission before merge
- **AND** the project documentation states this expectation in CONTRIBUTING

### Requirement: Contributor docs cover the dev loop

The repository SHALL include a `backend/README.md` that documents how to install dependencies, run the service, run tests, and lint the code.

#### Scenario: Contributor follows backend README to first running service

- **WHEN** a new contributor reads `backend/README.md` and follows the steps as written
- **THEN** they reach a running `/health` response without needing to ask the team

### Requirement: Docker images suitable for offline dev

The backend Docker image SHALL build and run without requiring credentials to private registries or external services.

#### Scenario: Backend image builds offline-capable

- **WHEN** `docker compose build` runs against this repository
- **THEN** the build succeeds using only the public Python base image and the declared dependencies
