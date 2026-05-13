# Anti-pattern rules engine

A rule looks at a `Diagram` and emits `Finding`s when something's off. It's pure Python — no LLM involved, no network, deterministic.

If you want to add a new rule, this README is what you need.

## What a rule looks like

A rule is any class with four class-level attributes and a `check` method:

```python
from app.schemas.diagram import Diagram
from app.schemas.finding import Finding, Severity


class MyRule:
    id = "my-rule"                     # kebab-case, unique
    severity = Severity.WARNING        # ERROR | WARNING | INFO
    title = "Short user-facing title"
    description = "Why this matters. Pedagogical. The LLM will use this verbatim."

    def check(self, diagram: Diagram) -> list[Finding]:
        # Walk the diagram, return zero or more Findings.
        return []
```

You don't inherit from anything. The shape *is* the contract — Python's `Protocol` checks it for you. If the contract test in `tests/test_rule_contract.py` passes for your rule, you're done.

## Severity guide

| Severity   | Meaning                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------ |
| `ERROR`    | This is wrong. The diagram should not look like this. (Direct frontend-to-database, etc.)        |
| `WARNING`  | This is usually wrong. The user might have a reason but should know. (Missing auth, cycles, etc.) |
| `INFO`     | Heads-up that doesn't block anything. (No rules at this level yet.)                              |

Pick the highest severity you're confident about. False positives at `ERROR` level are very expensive — they teach users to ignore the engine. Prefer `WARNING` if you're not sure.

## How to add a rule

1. **Create `app/services/rules/rules/<your_rule>.py`** with one class following the shape above. Keep it focused: one rule per file.
2. **Register it** by adding two lines to `app/services/rules/registry.py`:
   - Import your class.
   - Append an instance to `_BUILT_IN_RULES`.
3. **Add a test** at `backend/tests/test_rule_<your_rule>.py` with at minimum:
   - One diagram that *should* trigger the rule, asserting on the finding count and node/edge IDs.
   - One diagram that *should not* trigger it, asserting zero findings.
4. **Run the suite** locally: `pytest`. CI runs the same.

That's it. No registration metadata, no plugin manifest, no entry points.

## When NOT to add a rule

- If detecting the issue requires LLM-level judgement ("is this component name well-chosen?"). That belongs in the prompt layer, not here.
- If the rule has a high false-positive rate on perfectly fine architectures.
- If the rule is a personal style preference rather than a structural mistake.

A rule earns its place by being precise. Ten precise rules beat fifty noisy ones.

## Conventions

- Rule IDs are kebab-case and start with the action: `no-direct-frontend-to-database`, `frontend-with-db-needs-auth`, `cycle-detected`.
- `description` is one to three sentences, in the tone of mentoring a junior. The LLM will read it; so will users.
- Findings carry `node_ids` and `edge_ids` so a future UI can highlight the offending parts of the diagram. Always include them when relevant.
- Don't import `httpx` or any LLM SDK. Rules are pure functions over the diagram.

## Reading the existing rules

If you want a template, the five built-in rules are short:

- `no_direct_frontend_to_database.py` and `no_direct_frontend_to_storage.py` — pattern matching over edge endpoints.
- `frontend_with_db_needs_auth.py` — checks for the presence/absence of node types.
- `isolated_node.py` — checks which nodes are referenced by edges.
- `cycle_detected.py` — the only non-trivial one; iterative DFS with coloring.
