# Contributing to Tangram

Thanks for considering a contribution. This guide is short on purpose.

## Before you write code

Tangram uses **[OpenSpec](https://openspec.dev)** as a planning layer between ideas and code. Non-trivial changes include a proposal in `openspec/changes/<change-id>/`. The proposal can live in the same PR as the implementation — see step 3 below.

**What counts as non-trivial?**

| Trivial (no proposal needed)               | Non-trivial (proposal needed)                      |
| ------------------------------------------ | -------------------------------------------------- |
| Typo, copy fix, dead-code removal          | Adding an LLM provider                             |
| Bug fix with a clear root cause            | Changing the diagram schema                        |
| Dependency bump                            | New API endpoint                                   |
| Test for existing behavior                 | UX change to the editor                            |
| Doc improvement                            | New configuration surface                          |

If unsure, default to writing a proposal. It takes 15 minutes and saves re-review later. The proposal does not have to be in its own PR.

## The OpenSpec workflow

### 1. Install the CLI

```bash
npm install -g @fission-ai/openspec@latest
```

(You can read `openspec/` markdown without it, but you'll want it to create new proposals.)

### 2. Propose

If you use Claude Code, Cursor, or GitHub Copilot, the slash command does the work for you:

```
/opsx:propose Add support for the Mistral provider
```

This generates `openspec/changes/add-mistral-provider/` with `proposal.md`, `design.md`, and `tasks.md`.

If you use another tool, run the CLI manually:

```bash
openspec new change "add-mistral-provider"
openspec instructions proposal --change "add-mistral-provider"
# ... then write proposal.md, design.md, tasks.md by hand
```

### 3. Open a PR

For most changes: **one PR with proposal + implementation together** is fine and preferred. Reviewers see the intent and the code at the same time, in the same place.

Split into two PRs (proposal first, implementation later) **only** when:

- The approach is uncertain and you want feedback before writing code.
- The change is large enough that one PR would be unreviewable (>500 lines of substantive code).
- Multiple contributors will pick up different parts.
- It is a breaking change that affects external users.

If unsure, default to one PR. Splitting later is cheap; merging two unnecessary PRs is wasteful.

### 4. Implement

If the proposal lives in the same PR as the code, implement as you go and check off tasks in `tasks.md` as they land.

If you split into a proposal-only PR first, run `/opsx:apply` on a follow-up branch once the proposal merges and open a second PR with the implementation.

### 5. Archive after merge

Once the implementation merges:

```
openspec archive add-mistral-provider
```

The proposal's specs roll into `openspec/specs/`, becoming the new ground truth. Open a small follow-up PR with the archive change.

## Code conventions

- Backend: Python 3.11+, FastAPI, Pydantic v2. Format with `ruff format`. Lint with `ruff check`.
- Frontend: TypeScript strict mode, Next.js, React Flow. Format with `prettier`. Types are auto-generated from the backend's OpenAPI — never hand-write API types in `frontend/types/api.ts`.
- Commits: imperative present ("add provider", not "added provider").
- PRs: link the proposal (`Closes openspec/changes/<id>`).
- **Configuration**: every new field on `backend/app/core/config.py:Settings` MUST be added to `backend/.env.example` with a placeholder or default. PRs that miss this will be flagged in review.
- **No new infrastructure dependencies** (Postgres, Redis, etc.) without an ADR. The MVP runs on `pip install + uvicorn` with no Docker. Adding a service is a deliberate architectural decision.

## Architecture decisions

For changes that constrain *many future changes* (stack, patterns, cross-cutting infrastructure), write an ADR in `docs/architecture/` alongside the proposal. See the [ADR index](./docs/architecture/README.md).

## Code of conduct

Be kind. Assume good faith. The maintainers reserve the right to remove anyone who makes the project unwelcoming.

## License

By contributing, you agree your contributions are licensed under the MIT license, the same as the project.
