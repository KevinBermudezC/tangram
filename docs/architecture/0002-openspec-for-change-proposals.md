# ADR-0002 — OpenSpec for change proposals

**Status:** Accepted

**Date:** 2026-05-09

**Decision-makers:** Tangram core team

**Supersedes:** —

**Related:** [ADR-0001 — Guardrails strategy](./0001-guardrails-strategy.md)

---

## Context

Tangram is open source. We expect contributors to come and go, and many of them will use AI assistants (Claude Code, Cursor, GitHub Copilot, etc.) to write code. Two recurring problems in projects like this:

1. **Lost context.** A contributor lands a change, leaves, and three months later nobody remembers *why* it was done that way. The git log shows the *what*; the *why* dies in a private chat or someone's head.
2. **AI assistants without ground truth.** When a contributor's AI assistant generates code, it has no project-specific context beyond the codebase itself. It can't see why we picked the tradeoffs we picked. So it suggests reasonable-but-wrong things, and the contributor merges them.

We need a lightweight planning layer that:
- Lives in the repo (not in chat, tickets, or someone's brain).
- Is readable by both humans and AI assistants.
- Captures *intent* and *tradeoffs* before code is written.
- Doesn't add so much process that it scares off casual contributors.

We already have ADRs for *architectural* decisions (single, rare, durable). We don't have a place for *change proposals* (frequent, evolutionary).

## Decision

Adopt **OpenSpec** (<https://openspec.dev>) as the change-proposal layer.

The CLI was installed and initialized with:

```bash
npm install -g @fission-ai/openspec@latest
openspec init --tools claude,cursor,github-copilot
```

This created:

- `openspec/specs/` — current state of accepted feature specs (empty until first archive).
- `openspec/changes/` — in-flight change proposals, each with `proposal.md`, `design.md`, `tasks.md`, `specs/`.
- `.claude/`, `.cursor/`, `.github/` — slash commands (`/opsx:propose`, `/opsx:apply`, `/opsx:archive`, `/opsx:explore`) and skill files for the supported AI assistants.

### Three-layer model

| Layer            | Lives in                    | Cardinality      | Used for                                                        |
| ---------------- | --------------------------- | ---------------- | --------------------------------------------------------------- |
| **ADRs**         | `docs/architecture/`        | Few, durable     | Architectural decisions: stack, patterns, cross-cutting choices |
| **OpenSpec**     | `openspec/`                 | Many, evolving   | Feature/change proposals: what we're building next and why      |
| **Pydantic/SDD** | `backend/app/schemas/`      | Per data type    | Runtime data contracts (Diagram, Node, Edge…)                   |

### Workflow for contributors

1. **Propose** a change: `/opsx:propose <description>` — generates `proposal.md`, `design.md`, `tasks.md` under `openspec/changes/<change-id>/`.
2. **Discuss** the proposal in a PR before any code is written.
3. **Apply**: `/opsx:apply` — implement the change against the proposal.
4. **Archive**: `/opsx:archive <change-id>` — once merged, the proposal's specs roll into `openspec/specs/`.

The slash commands work in Claude Code, Cursor, and GitHub Copilot. Contributors using other tools can run the equivalent CLI directly (`openspec new change`, `openspec instructions`, `openspec archive`).

### Boundary with ADRs

- **ADR** if the decision is architectural and likely to constrain *many future changes* (e.g. "use Postgres + pgvector", "BYOK + Ollama for LLM providers", "guardrails strategy").
- **OpenSpec change proposal** if the decision is about implementing or evolving a feature (e.g. "add LLM provider abstraction", "ship POST /generate endpoint", "introduce reactive AI mode").

When an OpenSpec proposal forces a *new* architectural decision, write an ADR alongside the proposal and link them.

## Consequences

### Positive

- Contributors arrive and find the *intent* of recent changes already in the repo, alongside the code.
- AI assistants (used by us and by contributors) can read `openspec/` for ground truth instead of inferring from code.
- PR review shifts from "is this code correct?" to "is the proposal correct, *and* is this code correct?" — catches design errors earlier.
- Living documentation that doesn't depend on a wiki, Notion, or Linear that contributors may not have access to.
- Eats own dogfood: Tangram is an AI-assisted product built with an AI-assisted spec workflow — coherent narrative for the README and marketing.

### Negative

- Adds a process layer. Contributors must be willing to write a short proposal before coding non-trivial changes. The bar is "non-trivial": typo fixes and small bug fixes don't need proposals.
- Another global dependency (`@fission-ai/openspec`). Contributors who don't install it can still read `openspec/` markdown, but can't use the slash commands. Acceptable.
- Risk of stale specs. If a proposal is merged but then quietly deviated from in code, the spec lies. Mitigation: `/opsx:archive` is mandatory before closing a feature PR; spec updates are part of the change.
- We will need to enforce the workflow in PR review until it becomes habit. Not free.

## Alternatives considered

### A. ADRs only (status quo before this decision)

**Rejected.** ADRs are right-sized for architectural decisions but too heavy for "I want to add this feature." We'd write fewer of them, lose context faster, and get nothing for our contributors' AI assistants.

### B. Issue tracker as the source of truth

**Rejected.** Issues are not version-controlled with the code. They drift from reality. They're not readable by AI assistants without extra integrations. They're not searchable in the same `git grep` as the code.

### C. Free-form `docs/proposals/`

**Rejected.** Without a tool enforcing structure, proposals would diverge in format and decay over time. OpenSpec's CLI enforces a consistent shape and integrates with the AI tools contributors are already using.

### D. Wait until we have more contributors

**Rejected.** The cost of adopting OpenSpec early is one ADR (this one) and a few config files. The cost of adopting it later, once habits are formed, is much higher. Adopt now, refine as we go.

## References

- OpenSpec — <https://openspec.dev>
- OpenSpec on GitHub — <https://github.com/Fission-AI/OpenSpec>
- ADR-0001 — Guardrails strategy
