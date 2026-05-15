## Context

Every previous proposal has been a *building block*. This one is the first *assembly*. It pulls four other capabilities into one entry point:

- `component-metadata` → injected as compact summaries (always)
- `patterns-library` + `pattern-retrieval` → top-k retrieved patterns
- `anti-pattern-rules` → findings appended when a diagram is supplied
- `llm-providers` → the `ChatMessage` shape downstream callers will send

If we don't centralize this, every endpoint reinvents the wheel — and the LLM sees subtly different context on different code paths. That's how prompt drift starts. This file is the firewall against it.

## Goals / Non-Goals

**Goals:**

- One public function: `compose_prompt(user_request, diagram=None, mode_id="tutor", k_patterns=3)`. Every future endpoint uses it.
- The mode (persona) is loaded from a markdown file, parallel to how patterns are loaded. The system prompt itself is contributor-editable without Python.
- Composition deterministic given the same inputs (same `Settings`, same corpus). Two calls with identical args produce the same message list (modulo retrieval order ties).
- Errors in any sub-layer (retrieval down, rules raising) degrade gracefully. We never block the LLM call because a peripheral capability misbehaved.
- The "tutor" system prompt is genuinely good — short, opinionated, pedagogical, second person, references the injected context explicitly so the LLM uses it.

**Non-Goals:**

- HTTP endpoints. They consume this in their own proposals.
- Multiple modes. One seed mode (`tutor`); the loader will accept more, but we don't ship them.
- Prompt optimization (token counting, smart truncation). Out of scope; today's corpus + 3 retrieved patterns is comfortably under any model's context window.
- Conversation memory / multi-turn. `compose_prompt` is single-turn for MVP.
- Tool-use composition. The LLM provider abstraction supports tools; wiring them is endpoint-level work.

## Decisions

### Modes as markdown with frontmatter, mirroring patterns

`modes/tutor.md` looks like:

```markdown
---
id: tutor
title: Tutor
summary: Pedagogical persona for junior developers learning system design.
---

You are Tangram, a system-design tutor for junior developers.
...
```

Same parser (`python-frontmatter`), same file-layout rules, same enforce-id-matches-filename invariant. Contributors who know patterns know modes.

**Alternatives considered**: hardcoded Python strings (rejected — prompts get edited often; non-Python contributors should be able to tune them), YAML (rejected — multi-paragraph prose in YAML is painful to read).

### Single composer function, optional diagram argument

```python
async def compose_prompt(
    user_request: str,
    diagram: Diagram | None = None,
    mode_id: str = "tutor",
    k_patterns: int = 3,
) -> list[ChatMessage]:
```

When `diagram is None` (used by `/generate`), we skip rule findings and the diagram serialization. When a diagram is supplied (used by `/analyze`, future reactive mode), we include both.

**Alternatives considered**: separate `compose_for_generation` and `compose_for_analysis` functions (rejected — 80% of the logic is shared; two entry points invite divergence).

### Always include all 8 component summaries

Every call injects a compact (~50 tokens each) summary of all 8 component types. Why not filter by what's relevant to the diagram?

- For `/generate`, there's no diagram yet — the LLM needs to know the full vocabulary it can pick from.
- For `/analyze`, the diagram is given but the model may still benefit from knowing what *wasn't* used (e.g. to suggest adding a queue).
- The total cost is ~400 tokens. Negligible.

We use a *compact* summary (label + description + 2-3 tradeoffs), not the full YAML. The full YAML lives in `components/` and is too verbose for prompt injection.

**Alternatives considered**: filter by diagram's node types (rejected — costs nothing to include all 8, gains nothing to filter), full YAML inline (rejected — wasteful, would dominate the context).

### Retrieval is best-effort

The composer calls `retrieve_patterns(user_request, k_patterns)`. If it returns `[]` (because Chroma is down or Ollama isn't running), we proceed without retrieved patterns. The composer's job is to *not* block on retrieval failure — this matches the graceful-degradation requirement of the retrieval layer.

**Alternatives considered**: require non-empty retrieval (rejected — couples this layer's reliability to two infrastructure dependencies).

### One system message, structured by section separators

The composed system message is a single string with `---` separators between sections:

```
<mode system prompt>

---

# Component vocabulary

<compact summaries>

---

# Relevant patterns

<retrieved patterns>

---

# Static analysis findings  (only if diagram supplied)

<rule findings>
```

Followed by the user message containing the request + (optional) serialized diagram.

**Why one system message**: most LLMs handle multiple system messages inconsistently. One concatenated message is portable across Ollama, OpenAI, and Anthropic.

**Why `---` separators**: visually clear in the prompt; LLMs respect the structural cue without needing explicit instruction.

**Alternatives considered**: separate `system` messages per section (rejected — provider-inconsistent behavior), one mega-system message without separators (rejected — model conflates sections).

### Rule findings as a structured-but-prose block

When a diagram is supplied, we run `check_all(diagram)` and append a section like:

```
# Static analysis findings

The following structural issues were detected (these are pre-LLM, deterministic):

- [ERROR] Frontend "Customer app" connects directly to database "Orders DB". (Rule: no-direct-frontend-to-database)
- [WARNING] Diagram has frontend + database but no auth node. (Rule: frontend-with-db-needs-auth)
```

This frames findings as **inputs** to the LLM, not as authoritative output. The LLM then explains them to the user in the mode's tone.

**Alternatives considered**: pass findings as a JSON payload in the user message (rejected — fights the natural-language flow of the prompt).

### Mode loading reuses the patterns loader pattern

`load_modes()`, `get_mode()`, `reset_for_tests()` — same shape as `load_patterns()`. `lru_cache`-d, validated against `Mode` schema, frontmatter-driven. A future contributor who's worked on patterns or components recognizes this instantly.

## Risks / Trade-offs

- **Risk**: the tutor system prompt drifts in tone over edits and contradicts other curated content. → **Mitigation**: PR review on `modes/tutor.md`; tone guidance documented in `modes/README.md`.
- **Risk**: the composer becomes a god-function as we add more sources. → **Mitigation**: each section is built by a private helper. Adding section #6 means adding one helper, not rewriting the function.
- **Risk**: rule findings + retrieved patterns + components + system prompt + diagram blow past context windows on small models. → **Mitigation**: today's combined size is ~3-5k tokens, well under every supported model's window. Truncation logic ships when we have evidence of a problem.
- **Risk**: `compose_prompt` runs four sub-systems on every call (mode load, components load, patterns retrieve, rules check). → **Mitigation**: every sub-system is cached or fast. Total cost dominated by the retrieval embedding call.
- **Trade-off**: this proposal is wider than usual (touches schemas, services, modes, prompts, tests, docs). We accept that because the composer is the first integration point and it's worth landing as one coherent change rather than three half-PRs.

## Migration Plan

No migration. New package. Rollback = revert.

## Open Questions

- **Should the composer return token-counting metadata?** Useful for the future eval suite. Out of scope; trivial to add later.
- **Should `tutor.md` reference itself in third person?** I picked second person ("You are Tangram") because that's what the LLM literature recommends. Easy to swap if it reads weird in practice.
- **Should we cache composed prompts?** Probably not — the user request varies, retrieval varies, no two calls hit the same composition. Cache the *sub-components* (mode, components, patterns), not the assembled prompt.
