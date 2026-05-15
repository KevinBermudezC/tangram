## MODIFIED Requirements

### Requirement: Pull request CI

The repository SHALL run continuous integration checks automatically on every pull request targeting `main`. The CI run SHALL report at least four distinct status checks (lint, test, openspec, frontend) that a reviewer can see without leaving the PR page.

#### Scenario: PR opened triggers CI

- **WHEN** a contributor opens a pull request targeting `main`
- **THEN** GitHub Actions starts a workflow run for that PR
- **AND** the PR page shows pending checks for lint, test, openspec, and frontend within seconds

#### Scenario: New commits re-run CI

- **WHEN** a contributor pushes additional commits to an open PR branch
- **THEN** GitHub Actions starts a new workflow run for the latest commit
- **AND** the PR page reflects the new run's status

## ADDED Requirements

### Requirement: Frontend CI job

The CI workflow SHALL include a `frontend` job that runs on the same triggers as the existing Python jobs. The job SHALL execute `npm ci`, `npm run lint`, `npm run typecheck`, and `npm run test` from the `frontend/` directory. Any failure of those subcommands SHALL fail the job.

#### Scenario: Failing TypeScript fails the job

- **WHEN** a PR introduces a TypeScript error in `frontend/`
- **THEN** the `frontend` job exits non-zero
- **AND** the failing output identifies the file and the type error

#### Scenario: Frontend lint violation fails the job

- **WHEN** a PR introduces code that fails an ESLint rule in `frontend/`
- **THEN** the `frontend` job exits non-zero
- **AND** the failing output identifies the rule and the offending line

#### Scenario: Failing frontend test fails the job

- **WHEN** a PR introduces a code change that breaks a frontend test
- **THEN** the `frontend` job exits non-zero
- **AND** the failing output shows the test name and assertion
