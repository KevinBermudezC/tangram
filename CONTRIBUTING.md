# Contributing

Thanks for thinking about helping. This is a small project run by one person (so far), so I'll be honest: the workflow is what works for me and might evolve as more contributors show up. If something feels weird, open an issue and let's talk.

## The short version

- **Trivial change?** Open a PR. Typos, doc tweaks, dependency bumps, simple bug fixes — just send the diff.
- **Non-trivial change?** Write a quick proposal first (it can be in the same PR as the code). Adding an LLM provider, changing the diagram schema, a new endpoint, a UX change — these all need a proposal.
- **If in doubt:** lean toward writing a proposal. It's 15 minutes and saves both of us re-review later.

Below is the slightly longer version.

## Editing components and patterns (the easiest contributions)

If you don't want to touch Python, **the [`components/`](./components/) folder is where you can have the most impact fastest**. Each YAML file describes one architectural component (database, queue, etc.) — what it is, tradeoffs, common anti-patterns. The LLM reads these when explaining a diagram.

Good contributions:
- Fixing a bad tradeoff or anti-pattern that doesn't ring true to you
- Adding a missing implementation example (`SQLite` to `database.yaml`'s list, etc.)
- Sharpening prose — these are read by juniors, clarity matters

Just open a PR with the edit. CI will validate the schema; I'll review the content.

The same will be true for the upcoming `patterns/` folder.

## OpenSpec workflow (for non-trivial changes)

We use [OpenSpec](https://openspec.dev) to keep a written record of *why* each change happened. The tool was designed for AI-assisted dev workflows — proposals double as instructions for AI coding agents, which means contributors using Cursor, Claude Code, or GitHub Copilot get a head start.

### 1. Install the CLI

```bash
npm install -g @fission-ai/openspec@latest
```

Reading the proposals doesn't need the CLI, but creating new ones does.

### 2. Create the proposal

If you're in Claude Code, Cursor, or VS Code with Copilot:

```
/opsx:propose Add support for the Mistral provider
```

That generates the proposal scaffold under `openspec/changes/add-mistral-provider/`. Fill in `proposal.md`, `design.md`, the spec(s) and `tasks.md`. The format examples are in the existing changes — copy one as a template.

If you're using another tool, run `openspec new change "<name>"` and write the files by hand.

### 3. One PR by default

Proposal + implementation in the same PR is the default and what I prefer. The reviewer sees the intent and the code in one place.

Split into two PRs only when:
- The approach is genuinely uncertain and you want feedback before writing code.
- The change is too big for one PR (rough threshold: 500+ lines of substantive code).
- Two contributors will work on different parts.
- It's a breaking change for external users.

If you're not sure, default to one PR. Easier to split later than to merge two redundant ones.

### 4. Archive after merge

After the PR merges, run:

```
openspec archive <change-name>
```

This moves the specs from `openspec/changes/` into `openspec/specs/` (where they become the ground truth). Open a tiny chore PR with the archive change. Takes 2 minutes.

## Code conventions

**Backend (Python):**
- Python 3.11+, FastAPI, Pydantic v2.
- Format with `ruff format`. Lint with `ruff check`. Both run in CI.
- Tests with `pytest`. Network calls are mocked; no real LLM calls in CI.

**Frontend (TypeScript):**
- Node.js 20+, Next.js, React 19, React Flow.
- **Package manager: pnpm** (pinned via `packageManager` in `package.json`; auto-provisioned through `corepack enable`).
- TypeScript strict mode; types in `frontend/types/tangram.ts` mirror the backend Pydantic schemas (hand-written until codegen lands).
- ESLint flat config (`@eslint/js` + `typescript-eslint`). Tests with Vitest + Testing Library.
- From `frontend/`: `pnpm lint`, `pnpm typecheck`, `pnpm test`. CI runs all three.

**Commits:** imperative present tense (`add provider`, not `added provider`). Use [conventional-commit](https://www.conventionalcommits.org/) prefixes (`feat`, `fix`, `chore`, `docs`, `refactor`). Scope optional but appreciated: `feat(llm): add Mistral adapter`.

**PRs:** link the proposal in the description (`Closes openspec/changes/<id>`). The PR template will guide you.

**Configuration:** if you add a field to `backend/app/core/config.py:Settings`, you also add it to `backend/.env.example`. CI doesn't enforce this yet, but reviewers will flag it.

**No new infrastructure dependencies** (Postgres, Redis, etc.) without an ADR first. Currently the whole project runs with `pip install + uvicorn`, no Docker. That's a feature for contributors, and I'd like to keep it that way unless we have a strong reason.

## ADRs

If your change introduces an architectural decision that'll affect many future changes — choosing a database, adopting a new framework, changing how persistence works — write an ADR in `docs/architecture/` alongside the proposal. Use the existing ADRs as templates. They're short (1-3 pages) and focused on *why* over *how*.

The [ADR index](./docs/architecture/README.md) lists all of them.

## Repository protections

`main` is protected. Nobody pushes to it directly, including me. All changes flow through PRs, get reviewed (currently by me, eventually by Code Owners listed in `.github/CODEOWNERS`), and have to pass CI.

The full ruleset and rationale is in [`docs/repo-setup.md`](./docs/repo-setup.md) if you're curious.

## What I look for in reviews

- **The proposal is honest about scope.** "Non-goals" is the most useful section in any proposal. If I see a non-goals list, I trust the author understood the boundary.
- **The code reads top-to-bottom.** Imports clean, names clear, comments where the *why* is non-obvious. Skip comments that just restate the code.
- **Tests cover the contract, not the implementation.** "What does this function promise?" answered by tests, ideally one assertion per test.
- **The PR is honest about what works and what doesn't.** "Verified locally: ruff + pytest pass. Did NOT test against real Anthropic API." Better than silence.

## Code of conduct

Be kind. Assume good faith. Disagree on the merits, not the person. I'll remove anyone making the project unwelcoming.

## License

By contributing, you agree your contributions are licensed under MIT, the same as the project.

---

**Honest note:** I drafted this guide with help from an AI, then heavily edited. If something feels generic or doesn't match how things actually work, open an issue. The contract should match reality.
