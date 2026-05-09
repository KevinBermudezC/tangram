# Architecture Decision Records

This folder contains ADRs — short documents that capture significant architectural decisions, the context behind them, and the alternatives we considered.

## Why we write ADRs

- Future contributors can understand *why* the codebase looks the way it does, not just *what* it does.
- Decisions get reviewed before they get implemented.
- We avoid re-litigating the same debates every six months.

## Format

Each ADR follows a lightweight template:

- **Status** — proposed / accepted / deprecated / superseded
- **Context** — what problem are we solving and what constraints matter
- **Decision** — what we're doing
- **Consequences** — good and bad outcomes we accept
- **Alternatives considered** — options we rejected and why

Numbered sequentially: `0001-…`, `0002-…`, etc.

## Index

| #    | Title                                                                | Status   |
| ---- | -------------------------------------------------------------------- | -------- |
| 0001 | [Guardrails strategy](./0001-guardrails-strategy.md)                 | Accepted |
| 0002 | [OpenSpec for change proposals](./0002-openspec-for-change-proposals.md) | Accepted |

## Writing a new ADR

1. Copy the most recent ADR file as a template.
2. Increment the number.
3. Open a PR. Discussion happens there.
4. Once accepted, add it to the index above.
