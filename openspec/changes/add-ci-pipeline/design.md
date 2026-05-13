## Context

We need CI that:

- Runs the same checks the developer runs locally (`ruff format`, `ruff check`, `pytest`, `openspec validate`).
- Reports per-check status so reviewers see which subsystem broke.
- Stays under a minute end-to-end, otherwise contributors will start ignoring it.
- Requires zero credentials and zero paid services — GitHub Actions on a public repo is free.
- Does not need to test the frontend yet (there is no frontend code).

The 31 existing tests run in ~6 seconds locally. ruff lint runs in under a second. openspec validate is similarly fast. The bottleneck on CI will be dependency installation, which is what we cache.

## Goals / Non-Goals

**Goals:**

- Pull request CI: every PR sees three status checks (lint, test, openspec) with clear pass/fail.
- Push CI: same checks run on `main` after a merge, catching anything that slipped through.
- Repeatable, deterministic builds — pinned Python version, deterministic dependency install via `pip install -e ".[dev]"`.
- Fast: total wall-clock under one minute for cache hits, under two for cache misses.

**Non-Goals:**

- Frontend CI. Lands with `establish-frontend-foundation`.
- Coverage reports. Phase 2 once we have meaningful test surface.
- Matrix testing across Python versions. Phase 2 if we ever need to support 3.11 and 3.12 simultaneously; for now we only support what the Dockerfile specifies.
- Deployment, container image building, image scanning. We do not deploy from CI.
- Required status checks on the branch ruleset. The workflow has to run successfully first so the check names exist in GitHub; the owner adds them to the ruleset by hand afterwards.
- Concurrency cancellation across pushes on the same PR (nice-to-have, easy to add later).

## Decisions

### GitHub Actions over alternatives

We use GitHub Actions because the repo lives on GitHub, the runner is free for public repos, and the YAML config lives next to the code under `.github/workflows/`.

**Alternatives considered:** CircleCI / GitLab CI (rejected — extra account, extra integration), pre-commit hooks only (rejected — does not block bad PRs from being merged, only catches local commits), Buildkite (rejected — overkill, requires self-hosted runners).

### One workflow file, three parallel jobs

A single `ci.yml` with three jobs that run in parallel. Each job sets up Python, installs deps, runs one tool.

**Rationale:** parallel jobs give the contributor three independent status indicators in the PR UI. A red `lint` next to a green `test` immediately tells you where to look. A monolithic job would still pass/fail as one and obscure the cause.

**Alternatives considered:** one job with sequential steps (rejected — slower, less informative on failure), one workflow file per job (rejected — three files for what is conceptually one capability).

### Python 3.12 on `ubuntu-latest`

Matches the `python:3.12-slim` base in `backend/Dockerfile`. Ubuntu is the default GitHub runner and the cheapest in build minutes.

**Alternatives considered:** Python 3.11 (rejected — the Dockerfile pins 3.12), matrix on 3.11/3.12/3.13 (rejected — we do not support multiple Python versions yet; Phase 2 decision).

### `actions/setup-python@v5` with built-in pip cache

The official action supports `cache: 'pip'` and reads `pyproject.toml` for the cache key. Zero custom config, automatic invalidation when deps change.

**Alternatives considered:** custom cache step with `actions/cache@v4` (rejected — more YAML to maintain for the same outcome), no cache (rejected — every CI run reinstalls deps from scratch, wastes seconds).

### `openspec validate` for every active change, not just the one being added

The workflow validates every directory under `openspec/changes/`. If any active proposal is broken, CI fails. This catches the case where a contributor adds a new proposal while another is in flight and the second silently breaks the first.

**Alternatives considered:** validate only changed files (rejected — too clever, easy to miss edge cases; the cost of validating all proposals is negligible).

### Trigger on `pull_request` + `push: branches: [main]`

`pull_request` covers every contributor PR. `push: main` covers the post-merge state — useful for the badge in the README that says "build passing" and as a safety net for anything that snuck through despite required checks.

**Alternatives considered:** `pull_request` only (rejected — no signal on `main` health), `push: '**'` (rejected — runs CI on private branches, wastes minutes).

## Risks / Trade-offs

- **Risk**: ruff or pytest upgrade breaks CI silently. → **Mitigation**: pin lower bounds in `pyproject.toml`; SDK upgrades are deliberate PRs that show up in CI before merging.
- **Risk**: GitHub Actions changes its action API (`setup-python` major version bump). → **Mitigation**: pin to major version with `@v5`; review release notes when upgrading to `@v6`.
- **Risk**: A flaky test causes intermittent red CI. → **Mitigation**: investigate every failure; never `pytest --reruns` to paper over flakes. We do not have flakes today.
- **Risk**: The workflow's check names change in future edits and break the branch ruleset's required-checks list. → **Mitigation**: the ruleset rule is added *after* CI runs once and the names stabilize; subsequent renames are deliberate and documented.
- **Trade-off**: not using `concurrency` cancellation means a contributor force-pushing rapidly to a PR will queue multiple CI runs. Acceptable for our scale today; we add it when we feel the pain.

## Migration Plan

No migration. This is a new workflow. If it misbehaves, revert the PR.

## Open Questions

- **Should we add a `pre-commit` config so contributors run the same checks locally before push?** Useful, but a separate concern — out of scope here. Future proposal `add-pre-commit-config` if we want it.
- **Should CI fail when a new field is added to `Settings` but `.env.example` is not updated?** That rule is documented in CONTRIBUTING but not automated. Worth a small linter check in CI later.
- **Should we add caching for ruff itself?** ruff is fast enough that the cache cost exceeds the benefit. Skip.
