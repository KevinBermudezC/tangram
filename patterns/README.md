# Patterns library

This folder contains curated architectural patterns. Each markdown file describes one pattern: what it is, when to use it, when to avoid it, the components involved, the common pitfalls. The LLM consults these when explaining or generating diagrams.

If `components/` is "what is one piece?", `patterns/` is "how do pieces fit together?".

## File format

Each pattern lives at `patterns/<id>.md`. The file has YAML frontmatter at the top, then a markdown body.

```markdown
---
id: my-pattern
title: My Pattern
complexity: beginner    # beginner | intermediate | advanced
tags:
  - web
  - example
component_types:        # values from the NodeType enum
  - frontend
  - backend
  - database
---

# My Pattern

## What it is

One or two paragraphs describing the pattern at a high level.

## When to use

Bullet list of situations.

## When to avoid

Bullet list of situations.

## Components involved

Which Tangram component types take part, and what they do here.

## Common pitfalls

The mistakes a junior would make.
```

The five `##` sections are **required**. The loader rejects files missing any of them. Additional sections are fine.

## Frontmatter rules

- `id` must be lowercase kebab-case and must equal the filename stem (`my-pattern` in `my-pattern.md`).
- `title` is human-readable, capitalized.
- `complexity` is one of `beginner`, `intermediate`, `advanced`. Pick on the basis of "how much architectural background do I need to understand this".
- `tags` are free-form. No taxonomy is enforced; let it emerge.
- `component_types` lists every Tangram `NodeType` involved in the pattern. Validated against the enum, so typos fail loudly.

## Tone

Same as `components/`: mentor-to-junior, second person, opinionated, no jargon without payoff. Aim for 400–800 words per pattern. Shorter is better than padded.

Concrete > abstract. "Postgres + a single backend handle far more than newcomers expect" beats "use a scalable data layer".

## Adding a new pattern

1. Pick a kebab-case `id`. Check that `patterns/<id>.md` doesn't already exist.
2. Copy an existing pattern file as a template.
3. Fill in the frontmatter and the five required sections.
4. Run `pytest backend/tests/test_pattern_files.py` to confirm it loads and has the required sections.
5. Open a PR. The CI workflow will run the same checks on your branch.

You do not need to register the pattern anywhere else. The loader walks the directory and picks up every `.md` file (except this README) automatically.

## What lives here vs in `components/`

- A file in `components/` describes **one node type** (database, queue, etc.). Short, structured, factual.
- A file in `patterns/` describes **a recognizable arrangement of multiple nodes**. Longer, prose-heavy, opinionated.

If a contribution is "here's a clearer description of what a cache is", it belongs in `components/cache.yaml`. If it's "here's how to build a real-time chat system", it belongs in `patterns/realtime-chat.md`.

## Future: retrieval

Right now, the patterns library is loaded eagerly and any caller iterates over the dict it returns. A follow-up proposal (`add-rag-retrieval`) will add embeddings and a similarity-based retriever on top of this folder, so the LLM can ask for "patterns relevant to this user prompt" instead of receiving every pattern in context. The corpus format on disk stays the same; the retrieval layer is purely additive.
