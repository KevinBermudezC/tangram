# Contributing to Tangram

Thanks for considering a contribution. This guide is short on purpose.

## Before you write code

Tangram uses **[OpenSpec](https://openspec.dev)** as a planning layer between ideas and code. Non-trivial changes start with a proposal in `openspec/`, not with a PR full of code.

**What counts as non-trivial?**

| Trivial (no proposal needed)               | Non-trivial (proposal first)                       |
| ------------------------------------------ | -------------------------------------------------- |
| Typo, copy fix, dead-code removal          | Adding an LLM provider                             |
| Bug fix with a clear root cause            | Changing the diagram schema                        |
| Dependency bump                            | New API endpoint                                   |
| Test for existing behavior                 | UX change to the editor                            |
| Doc improvement                            | New configuration surface                          |

If unsure, open a discussion or draft proposal. We'd rather discuss for ten minutes than re-review a hundred lines.

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

### 3. Open a PR with the proposal only

Title it `proposal: add-mistral-provider`. Reviewers focus on intent, not implementation. Keep it small.

### 4. Once the proposal is merged, implement

```
/opsx:apply
```

Follow the tasks. Open a second PR with the implementation. Reviewers check that the code matches the proposal.

### 5. Archive

After the implementation PR merges:

```
/opsx:archive add-mistral-provider
```

The proposal's specs roll into `openspec/specs/`, becoming the new ground truth.

## Code conventions

- Backend: Python 3.11+, FastAPI, SQLModel, Pydantic v2. Format with `ruff format`. Lint with `ruff check`.
- Frontend: TypeScript strict mode, Next.js, React Flow. Format with `prettier`. Types are auto-generated from the backend's OpenAPI — never hand-write API types in `frontend/types/api.ts`.
- Commits: imperative present ("add provider", not "added provider").
- PRs: link the proposal (`Closes openspec/changes/<id>`).

## Architecture decisions

For changes that constrain *many future changes* (stack, patterns, cross-cutting infrastructure), write an ADR in `docs/architecture/` alongside the proposal. See the [ADR index](./docs/architecture/README.md).

## Code of conduct

Be kind. Assume good faith. The maintainers reserve the right to remove anyone who makes the project unwelcoming.

## License

By contributing, you agree your contributions are licensed under the MIT license, the same as the project.
