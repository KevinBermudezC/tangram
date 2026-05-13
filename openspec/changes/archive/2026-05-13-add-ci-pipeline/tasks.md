## 1. Workflow file

- [x] 1.1 Create `.github/workflows/ci.yml` with three jobs (`lint`, `test`, `openspec`) running in parallel
- [x] 1.2 Configure triggers: `pull_request` and `push: { branches: [main] }`
- [x] 1.3 Use `actions/checkout@v4` and `actions/setup-python@v5` with `python-version: '3.12'` and `cache: 'pip'`
- [x] 1.4 Install dev dependencies: `pip install -e ".[dev]"` from `backend/`
- [x] 1.5 Lint job runs `ruff format --check .` then `ruff check .` from `backend/`
- [x] 1.6 Test job runs `pytest` from `backend/`
- [x] 1.7 OpenSpec job installs `@fission-ai/openspec` via npm and validates every change under `openspec/changes/`

## 2. Documentation

- [x] 2.1 Add a "Continuous integration" section to `backend/README.md` describing the three checks and how to reproduce them locally
- [x] 2.2 Update `docs/repo-setup.md` to flag that the three check names (`lint`, `test`, `openspec`) become available for the branch ruleset's required-status-checks rule once CI has run successfully once
- [x] 2.3 Add a CI badge to the top-level `README.md` referencing the workflow

## 3. Verification

- [ ] 3.1 Locally verify the workflow YAML syntax by running it through GitHub Actions's UI on the PR (no local equivalent without `act` — defer)
- [x] 3.2 Confirm `openspec validate add-ci-pipeline --strict` passes locally
- [ ] 3.3 Confirm the workflow runs green on the PR opened from this branch
