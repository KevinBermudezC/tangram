## Context

We need a way to store curated architectural-pattern documents that are:

- **Editable without Python knowledge** — patterns are the front door for non-code contributions.
- **Structurally consistent** — the LLM needs to extract sections reliably.
- **Searchable by metadata** — even before RAG, we want to filter "patterns that involve a queue" or "beginner-complexity patterns".
- **Free-form in body** — the prose can't be over-constrained or quality drops.

Markdown with YAML frontmatter is the standard solution. Jekyll, Hugo, MDX, Astro all use it. `python-frontmatter` is the canonical parser for Python: about 200 lines of code, pure-Python, in widespread use.

## Goals / Non-Goals

**Goals:**

- A frontmatter schema with the minimum fields needed: `id`, `title`, `complexity`, `tags`, `component_types`.
- Five seed patterns spanning the most common shapes a junior dev encounters: CRUD, JAMstack, background worker, realtime chat, event-driven.
- A loader that parses + validates every file once and caches the result.
- Body shape enforced by a validation pass that checks for required `##` headers. Authors are free to add more.
- `patterns/README.md` clear enough that a contributor can write a new pattern without reading Python.

**Non-Goals:**

- Retrieval. No embeddings, no Chroma, no vector search. Out of scope here — `add-rag-retrieval` does this next.
- Long-form linting (spelling, grammar, link checks). Future, possibly via a pre-commit hook.
- Versioning of patterns (`crud-application@v2`). The git history *is* the version.
- Localization. English only for MVP.
- Auto-generation of patterns from real architectures. Patterns are deliberately curated.
- Cross-pattern references / a pattern graph. If pattern A references pattern B, it's a plain link in the markdown body; no schema for it.

## Decisions

### Markdown + YAML frontmatter, parsed via `python-frontmatter`

```markdown
---
id: crud-application
title: CRUD Application
complexity: beginner
tags:
  - foundational
  - web
component_types:
  - frontend
  - backend
  - database
  - auth
---

# CRUD Application

## What it is

Most web apps start here...
```

`python-frontmatter` returns a dict for the frontmatter and a string for the body. We pipe the dict into a Pydantic model and validate.

**Alternatives considered:** TOML frontmatter (rejected — less common, slightly more verbose), JSON sidecar files (rejected — two files per pattern is friction), monolithic YAML catalogue (rejected — merge-conflict hell at scale).

### Required body sections enforced by the loader

Patterns must contain `## What it is`, `## When to use`, `## When to avoid`, `## Components involved`, `## Common pitfalls` (case-insensitive match on the first level-2 header per section). Loader scans body for these markers and raises if any are missing.

**Why:** the LLM relies on consistent section markers to extract relevant context. Without enforcement, the corpus drifts and prompt composition becomes brittle.

**Alternatives considered:** parse markdown AST and require specific structure (rejected — too clever for MVP; the simpler header-scan approach catches 99% of real failures), no enforcement (rejected — first contributor without these sections breaks every downstream use).

### `id` is the filename stem and the canonical key

`patterns/crud-application.md` has `id: crud-application` in its frontmatter, and the loader asserts they match. The id is what the LLM and the future RAG layer reference.

**Why:** filesystem-canonical IDs avoid a separate manifest file and prevent rename-without-update bugs.

**Alternatives considered:** UUIDs (rejected — useless for human writers/readers), titles as keys (rejected — duplicates, capitalization woes, escaping in URLs).

### `complexity` as a closed enum

Three levels: `beginner`, `intermediate`, `advanced`. Same rationale as Severity in the rules engine — three levels are enough, more invites pointless tuning.

**Alternatives considered:** numeric difficulty 1–10 (rejected — bikeshedding), no complexity at all (rejected — useful filter for `add-tutor-mode` later).

### `component_types` references the closed `NodeType` enum

Validating each entry in `component_types` against the existing `NodeType` enum means typos like `databse` fail loud at load time.

**Why:** the same justification as `common_pairings` in `component-metadata`. Consistency between the diagram model and the patterns library.

**Alternatives considered:** free-form list of strings (rejected — typos and drift).

### Loader caches via `@lru_cache`, same shape as `components/`

The patterns loader mirrors the components loader: `load_patterns()` is `lru_cache`-d, `get_pattern(id)` does a dict lookup, `reset_for_tests()` clears the cache. Same mental model for contributors who've seen one of them.

**Alternatives considered:** eager load at app startup (rejected — couples module import to disk I/O, harder to test in isolation).

### Pattern body kept as a string, not parsed further

The `Pattern` Pydantic model carries `body: str` (the raw markdown). We don't pre-parse it into sections. Callers extract what they need.

**Why:** the LLM consumes prose; structured section extraction is the LLM's job at prompt time, not the loader's job. Keeps the schema simple.

**Alternatives considered:** parse into `{intent, when_to_use, when_to_avoid, ...}` (rejected — premature schematization; the contract between authors and the schema would calcify).

### `tags` are free-form strings, not closed

Authors can tag patterns with anything: `web`, `event-sourcing`, `serverless`, `multi-tenant`. We don't enforce a taxonomy.

**Why:** early in a corpus's life, you don't know what taxonomy you need. Let it emerge from real patterns, formalize later if necessary.

**Alternatives considered:** closed tag enum (rejected — guaranteed to be wrong on day one).

## Risks / Trade-offs

- **Risk**: contributors write low-quality patterns. → **Mitigation**: PR review is the gate. The `patterns/README.md` documents tone expectations.
- **Risk**: `python-frontmatter` becomes unmaintained. → **Mitigation**: the library is small (~200 lines); we could vendor it in a half-day if needed. Frontmatter parsing is not where complexity hides.
- **Risk**: header-scan enforcement is too strict and rejects a valid pattern that uses a different structure. → **Mitigation**: we accept this for MVP. If a real pattern proves the rule wrong, we relax it then. Five seed patterns are enough to validate the shape.
- **Trade-off**: keeping body as a string means callers have to do their own extraction when they want a specific section. This is intentional. We've optimized for *flexibility of the corpus*, not *convenience of the caller*.

## Migration Plan

No migration. New directory, new files. Rollback = revert.

## Open Questions

- **Should we add a `last_updated` field to frontmatter or rely on git mtimes?** Defer; git is the source of truth.
- **Should `component_types` be required or optional?** Required for now — every meaningful pattern involves component types. Reconsider if a pattern proves abstract enough to not list any.
- **How long should pattern bodies be?** No hard limit. The five seeds are aiming for 400–800 words each: long enough to teach, short enough to compose into a prompt without dominating it.
