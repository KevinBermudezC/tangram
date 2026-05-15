# Modes

This folder defines the LLM's *persona* — how it talks, what it pays attention to, what it refuses to do. Each `<id>.md` file is one persona.

MVP ships one mode: `tutor`. Future modes (Phase 2) include `senior` (skeptical, anti-pattern focused) and `brainstorm` (suggests alternatives). Each plugs into the same prompt-composition machinery.

## File format

```markdown
---
id: tutor
title: Tutor
summary: One-line description of the persona.
---

<the literal system prompt the LLM will receive>
```

The body is the system prompt verbatim. Headers, lists, formatting all go through to the model as-is.

## Frontmatter rules

- `id` is lowercase kebab-case and must equal the filename stem.
- `title` is human-readable.
- `summary` is one short sentence (UI hint, model selector tooltip, etc.).

## Body rules

- Be short. 200-500 words is a healthy range. The model reads this on *every call*; you're paying for it in tokens forever.
- Define the persona clearly in the first paragraph.
- Reference what the model will receive alongside (component vocabulary, patterns, findings) explicitly, so it uses them.
- State what NOT to do, not just what to do.

## Adding a new mode

1. Copy `tutor.md` as a template.
2. Pick a kebab-case id; rename the file to match.
3. Edit frontmatter (title, summary) and body (the prompt itself).
4. Run `pytest backend/tests/test_mode_loader.py` to confirm it loads.
5. Open a PR.

The mode is automatically picked up by `load_modes()`; no Python registration step.

## Why prompts live in markdown, not Python

- Editing happens often; markdown is faster than Python string literals.
- Reviewers can compare prompt versions cleanly in `git diff`.
- Non-Python contributors can iterate on tone and content.
- The frontmatter gives us structured metadata without polluting the prompt body.
