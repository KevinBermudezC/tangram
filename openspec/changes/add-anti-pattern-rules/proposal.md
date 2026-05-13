## Why

The `add-component-metadata` proposal documents what each node type is and what anti-patterns surround it as prose for the LLM. That's useful for explanation but not for *detection*. We want Tangram to flag obvious architectural mistakes deterministically — no LLM call required, instant feedback, repeatable across runs, cheap.

A rules engine that inspects a `Diagram` and returns structured findings gives us:

- **Speed**: detection runs in microseconds. The `/analyze` endpoint (future) can include rule findings as context for the LLM without spending tokens to derive them.
- **Trust**: rule findings are deterministic. "Your frontend connects directly to the database" is the same finding every time, with the same rationale. LLMs cannot match that.
- **A contributor surface that doesn't need Python skill**: once the rule infrastructure exists, adding a rule is roughly "copy an existing rule, change the check function". The shape of a rule is small.

Without this layer, every diagram analysis depends entirely on the LLM noticing the issue, which is unreliable for structural problems that need a graph walk to detect.

## What Changes

- Add `backend/app/services/rules/` package:
  - `base.py` — `Rule` protocol, `Finding` and `Severity` schemas, helper functions.
  - `registry.py` — registers all built-in rules; exposes `all_rules()` and `check_all(diagram)`.
  - `rules/` subpackage with one file per rule:
    - `no_direct_frontend_to_database.py` (severity: error)
    - `no_direct_frontend_to_storage.py` (severity: error)
    - `frontend_with_db_needs_auth.py` (severity: warning)
    - `isolated_node.py` (severity: warning)
    - `cycle_detected.py` (severity: warning)
- Add `backend/app/schemas/finding.py` — Pydantic models for `Finding` and `Severity`. Lives in `schemas/` because it's a wire shape that future routers will return.
- Add tests for each rule (good diagram + bad diagram) and for the registry.
- Document the rule API in a new `backend/app/services/rules/README.md` so contributors can add rules without reading every file.

This proposal does **not** add the HTTP endpoint that returns findings. That ships with `add-diagram-analysis-endpoint`.

## Capabilities

### New Capabilities

- `anti-pattern-rules`: A deterministic static-analysis layer over the `Diagram` schema. Defines a `Rule` protocol, a registry of built-in rules, and the `Finding` wire shape. Built-in rules cover five concrete cases that are unambiguous architectural mistakes for the MVP component set. Adding a sixth rule is one file + one registry entry.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `backend/app/services/rules/` package; new `backend/app/schemas/finding.py`; new tests under `backend/tests/test_rule_*.py`.
- **Dependencies**: none new. `Finding` and `Severity` are pure Pydantic; rule logic is pure Python over the existing `Diagram` schema.
- **Configuration**: no new env vars. The rule registry is hard-coded in `registry.py`. Future work may make rules toggleable per project — out of scope here.
- **Documentation**: `backend/app/services/rules/README.md` (new) explaining how to add a rule. Short section in `backend/README.md` pointing at it.
- **Future proposals unblocked**: `add-diagram-analysis-endpoint` (`POST /analyze` returns rule findings + LLM commentary), `add-diagram-generation-endpoint` (can pass rule violations from a partially-built diagram as context to the LLM), the reactive editor mode in Phase 2 (lints diagrams as the user edits).
