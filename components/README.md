# Component metadata library

This folder contains one YAML file per architectural component type that Tangram knows about. The LLM consults these files when explaining a node, suggesting tradeoffs, or detecting anti-patterns. **Curating this library is one of the highest-leverage ways to contribute.**

## Format

Each file is at `components/<type>.yaml` where `<type>` exactly matches a value in the `NodeType` enum (see `backend/app/schemas/diagram.py`). The schema each file must satisfy lives at `backend/app/schemas/component.py`.

```yaml
type: <NodeType value>             # required, must equal the filename stem
label: <human-readable name>       # required, non-empty
description: |                     # required, 1-2 sentences
  Short summary of what this component is.

typical_implementations:           # required, non-empty list
  - PostgreSQL
  - MySQL

common_pairings:                   # required, non-empty list of NodeType values
  - backend

tradeoffs:                         # required, non-empty list of bullet sentences
  - You gain X; you pay Y.

anti_patterns:                     # required, non-empty list of bullet sentences
  - Do not do this because…

learning_resources:                # optional
  - https://link/to/canonical-docs

tags:                              # optional
  - stateful
```

## Tone guidance

Write as if mentoring a junior developer who is genuinely curious. The goal is **insight per sentence**.

- Second person ("you gain X"), not third.
- Specific over abstract: prefer "Postgres 16's JSONB" over "modern SQL features".
- Opinionated: if something is almost always wrong, say so plainly.
- No buzzwords without payoff: don't say "scalable" without saying what scales.
- Short sentences. The reader is learning; don't make them re-read.

## Adding a new component type

If you want to add a new component (say `serverless_function`):

1. Add the value to the `NodeType` enum in `backend/app/schemas/diagram.py`.
2. Add a row to the `Component types (v0)` table in `docs/schema/diagram-v0.md`.
3. Create `components/serverless_function.yaml` following the format above.
4. Run the test suite — `tests/test_component_parity.py` will confirm the new type has its file.

This requires a Python edit (the enum). If you want to propose the *content* of a new component without touching Python, open an issue with a draft YAML and a maintainer will wire the enum.

## Editing an existing component

The fastest way to contribute. Just open a PR editing the YAML. CI validates the schema; reviewers focus on the prose. Quality > completeness — better to add one well-considered anti-pattern than five vague ones.

## What lives here vs in `patterns/`

- `components/` describes **what a single component type is**. Short, factual, every diagram with that node will reference it.
- `patterns/` (Phase 2 proposal) describes **how multiple components combine into a recognizable architecture**: CQRS, event-driven, JAMstack, etc. Long-form, retrievable via RAG.

If your contribution is "Here's a tradeoff about databases", it belongs in `database.yaml`. If your contribution is "Here's how CQRS works", it belongs in `patterns/cqrs.md` (coming soon).
