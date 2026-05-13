"""Every built-in rule satisfies the Rule Protocol."""

from __future__ import annotations

from app.services.rules.base import Rule
from app.services.rules.registry import all_rules


def test_all_rules_satisfy_protocol() -> None:
    for rule in all_rules():
        assert isinstance(rule, Rule), f"{type(rule).__name__} does not satisfy Rule"


def test_rule_ids_are_unique() -> None:
    ids = [r.id for r in all_rules()]
    assert len(ids) == len(set(ids))
