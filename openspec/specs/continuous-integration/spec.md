# continuous-integration Specification

## Purpose
TBD - created by archiving change add-ci-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Pull request CI

The repository SHALL run continuous integration checks automatically on every pull request targeting `main`. The CI run SHALL report at least three distinct status checks (lint, test, openspec) that a reviewer can see without leaving the PR page.

#### Scenario: PR opened triggers CI

- **WHEN** a contributor opens a pull request targeting `main`
- **THEN** GitHub Actions starts a workflow run for that PR
- **AND** the PR page shows pending checks for lint, test, and openspec within seconds

#### Scenario: New commits re-run CI

- **WHEN** a contributor pushes additional commits to an open PR branch
- **THEN** GitHub Actions starts a new workflow run for the latest commit
- **AND** the PR page reflects the new run's status

### Requirement: Push-to-main CI

The repository SHALL run the same CI checks on every push to `main`, primarily as a post-merge safety net and to keep the build badge accurate.

#### Scenario: Merge produces a green build

- **WHEN** a pull request is merged into `main`
- **THEN** GitHub Actions starts a workflow run on the merge commit
- **AND** the run completes with all three checks green if the merged state is healthy

### Requirement: Lint check

The lint job SHALL run `ruff format --check .` and `ruff check .` against `backend/`. It SHALL fail the workflow if either command exits non-zero.

#### Scenario: Unformatted code fails CI

- **WHEN** a PR introduces a Python file that does not match `ruff format`
- **THEN** the lint job exits non-zero
- **AND** the failing output shows which files would be reformatted

#### Scenario: Lint rule violation fails CI

- **WHEN** a PR introduces code that fails any rule in the `pyproject.toml` `[tool.ruff.lint]` selection
- **THEN** the lint job exits non-zero
- **AND** the failing output identifies the rule and the offending line

### Requirement: Test check

The test job SHALL run `pytest` in `backend/` and SHALL fail the workflow if any test fails.

#### Scenario: Failing test fails CI

- **WHEN** a PR introduces a code change that breaks an existing test
- **THEN** the test job exits non-zero
- **AND** the failing output shows the failing test name and assertion

### Requirement: OpenSpec validation check

The openspec job SHALL run `openspec validate <change> --strict` for every directory under `openspec/changes/` that contains a `.openspec.yaml`. It SHALL fail the workflow if any active change fails validation.

#### Scenario: Malformed proposal fails CI

- **WHEN** a PR introduces a change whose `proposal.md` is missing the Capabilities section
- **THEN** the openspec job exits non-zero
- **AND** the failing output identifies the broken change name and the validation error

#### Scenario: Healthy proposals pass

- **WHEN** every directory under `openspec/changes/` validates strictly
- **THEN** the openspec job exits zero

### Requirement: Fast, deterministic CI

The total wall-clock time for a CI run SHALL be under two minutes for a cache miss and under one minute for a cache hit. Builds SHALL be deterministic — same inputs produce the same result.

#### Scenario: Cached install is fast

- **WHEN** a CI run reuses the pip cache from a previous run with the same `pyproject.toml`
- **THEN** the dependency installation step completes in under thirty seconds

#### Scenario: Determinism across runs

- **WHEN** a CI run is re-triggered on the same commit without code changes
- **THEN** the result (pass or fail) is identical to the previous run

