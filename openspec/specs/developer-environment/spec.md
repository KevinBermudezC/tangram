# developer-environment Specification

## Purpose
TBD - created by archiving change establish-mvp-foundations. Update Purpose after archive.
## Requirements
### Requirement: Frictionless local startup

A contributor with Python 3.11+ installed SHALL be able to clone the repository and start a working backend in three commands or fewer, without installing Docker.

#### Scenario: Fresh clone bootstraps successfully

- **WHEN** a contributor runs `pip install -e ".[dev]"` followed by `uvicorn app.main:app --reload` from `backend/` after a fresh clone
- **THEN** the backend starts without manual configuration steps
- **AND** `GET http://localhost:8000/health` returns 200

#### Scenario: Restart preserves on-disk data

- **WHEN** the contributor stops the backend and starts it again
- **THEN** any files under `data/` (diagrams, Chroma store) persist across restarts because they live on the host filesystem

### Requirement: Optional Docker for production

The backend SHALL provide a working `Dockerfile` for production deployments, but SHALL NOT require Docker for local development.

#### Scenario: Docker image builds successfully

- **WHEN** `docker build` runs against `backend/`
- **THEN** the build succeeds using only the public Python base image and the declared dependencies
- **AND** the image runs Uvicorn on port 8000 by default

#### Scenario: Local dev does not require Docker

- **WHEN** a contributor follows the documented local-dev steps in `backend/README.md`
- **THEN** at no point are they required to install Docker, Docker Desktop, or any container runtime

### Requirement: Configuration documented via `.env.example`

Every configurable surface in the backend SHALL be present in `backend/.env.example` with a placeholder or sensible default.

#### Scenario: New setting added without doc update fails review

- **WHEN** a pull request introduces a new field on `Settings` and does not update `.env.example`
- **THEN** review feedback flags the omission before merge
- **AND** the project documentation states this expectation in CONTRIBUTING

### Requirement: Contributor docs cover the dev loop

The repository SHALL include a `backend/README.md` that documents how to install dependencies, run the service, run tests, and lint the code, all without Docker.

#### Scenario: Contributor follows backend README to first running service

- **WHEN** a new contributor reads `backend/README.md` and follows the steps as written
- **THEN** they reach a running `/health` response without needing to ask the team
- **AND** no step in the documented path requires installing Docker

