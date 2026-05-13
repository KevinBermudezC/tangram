## 1. Schema

- [x] 1.1 Add `app/schemas/finding.py` with `Severity` (StrEnum: error / warning / info) and `Finding` (Pydantic model)
- [x] 1.2 Add a round-trip test for `Finding` in `tests/test_finding_schema.py`

## 2. Rule infrastructure

- [x] 2.1 Add `app/services/rules/__init__.py` re-exporting `Rule`, `all_rules`, `check_all`, `Severity`, `Finding`
- [x] 2.2 Add `app/services/rules/base.py` with the `Rule` `Protocol` (`runtime_checkable`)
- [x] 2.3 Add `app/services/rules/registry.py` with `all_rules()` and `check_all(diagram)`

## 3. Built-in rules (one file per rule under `app/services/rules/rules/`)

- [x] 3.1 `no_direct_frontend_to_database.py`
- [x] 3.2 `no_direct_frontend_to_storage.py`
- [x] 3.3 `frontend_with_db_needs_auth.py`
- [x] 3.4 `isolated_node.py`
- [x] 3.5 `cycle_detected.py`

## 4. Tests (one per rule + integration)

- [x] 4.1 `tests/test_rule_no_direct_frontend_to_database.py` — good + bad diagrams
- [x] 4.2 `tests/test_rule_no_direct_frontend_to_storage.py`
- [x] 4.3 `tests/test_rule_frontend_with_db_needs_auth.py`
- [x] 4.4 `tests/test_rule_isolated_node.py`
- [x] 4.5 `tests/test_rule_cycle_detected.py`
- [x] 4.6 `tests/test_rule_registry.py` — `all_rules()` returns five rules with expected IDs; `check_all` aggregates findings
- [x] 4.7 `tests/test_rule_contract.py` — every built-in rule instance is `isinstance(..., Rule)`

## 5. Documentation

- [x] 5.1 Add `backend/app/services/rules/README.md` — how to add a rule, severity guide, test layout
- [x] 5.2 Add a "Anti-pattern rules" section to `backend/README.md` pointing at the rules package and `check_all`

## 6. Verification

- [x] 6.1 `ruff format --check` clean
- [x] 6.2 `ruff check` clean
- [x] 6.3 `pytest` clean (42 prior + 25 new = 67 total, all passing)
- [x] 6.4 `openspec validate add-anti-pattern-rules --strict`
