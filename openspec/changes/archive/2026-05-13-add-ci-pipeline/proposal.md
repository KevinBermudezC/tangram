## Why

The backend already has 31 passing tests and a clean ruff baseline locally, but nothing enforces those checks on incoming pull requests. Without CI:

- Contributors (and the maintainer) can land PRs that pass on their machine and break on someone else's.
- Reviewers spend time pulling branches locally to verify what should be obvious.
- OpenSpec proposals can drift from their `--strict` validity between author and merge.

The roadmap places CI at MVP item #4 — after the LLM provider abstraction, before the feature work accelerates. Adding it now is the cheapest moment: the test suite is small enough to run in seconds, the linting baseline is clean, and there is no large backlog of stale PRs that would need fixing first.

## What Changes

- Add `.github/workflows/ci.yml` running on every pull request and every push to `main`.
- Three jobs in parallel: `lint`, `test`, `openspec`.
  - `lint` — `ruff format --check` and `ruff check` against `backend/`.
  - `test` — `pytest` against `backend/tests/`.
  - `openspec` — `openspec validate <every change in openspec/changes/> --strict`.
- Cache the pip install across runs to keep CI under a minute.
- Document the workflow in `backend/README.md` so contributors know what CI is doing.

This proposal does **not** wire CI as a required status check on the branch ruleset. That is one click in the GitHub UI, documented in `docs/repo-setup.md` to be done once the workflow has run successfully a few times and we trust the check names.

## Capabilities

### New Capabilities

- `continuous-integration`: A GitHub Actions workflow that, on every pull request and on every push to `main`, verifies that `ruff format`, `ruff check`, `pytest`, and `openspec validate` all pass. Defines the contract for what "green CI" means in this repository.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: one new file `.github/workflows/ci.yml`.
- **Dependencies**: none new at runtime. The `[dev]` extras in `pyproject.toml` already include `ruff` and `pytest`.
- **Infrastructure**: free for public repositories on GitHub-hosted runners. No new accounts needed.
- **Documentation**: short section in `backend/README.md` explaining the workflow.
- **Operational follow-up**: after this PR merges and the workflow runs successfully once, the repo owner adds the three check names to the `main protection` ruleset's "Require status checks" rule. Tracked as an open question in `docs/repo-setup.md`.
- **Future proposals unblocked**: every subsequent feature proposal now ships with CI signal automatically.
