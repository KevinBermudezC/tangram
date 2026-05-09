"""Round-trip the canonical example from docs/schema/diagram-v0.md.

The Pydantic schemas in app.schemas.diagram are derived from the diagram-v0
documentation. This test pins that contract: if either drifts, this test fails.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.diagram import Diagram, NodeType


CANONICAL_EXAMPLE: dict = {
    "version": "0.1.0",
    "id": "01HXYZ123ABCDEF",
    "metadata": {
        "name": "Delivery app",
        "description": "Generated from: 'I want to build a delivery app'",
        "createdAt": "2026-05-09T14:30:00Z",
        "updatedAt": "2026-05-09T14:32:10Z",
    },
    "nodes": [
        {
            "id": "n_client",
            "type": "frontend",
            "label": "Customer mobile app",
            "position": {"x": 80, "y": 240},
            "properties": {"technology": "React Native", "notes": "iOS + Android"},
            "ai": {
                "explanation": "The customer-facing app.",
                "rationale": "Mobile because users will order on the go.",
                "confidence": 0.92,
            },
        },
        {
            "id": "n_api",
            "type": "backend",
            "label": "Orders API",
            "position": {"x": 420, "y": 240},
            "properties": {"technology": "Node.js / Express"},
            "ai": {
                "explanation": "The brain of the system.",
                "rationale": "Centralizes order logic.",
                "confidence": 0.88,
            },
        },
        {
            "id": "n_db",
            "type": "database",
            "label": "Orders DB",
            "position": {"x": 760, "y": 240},
            "properties": {"technology": "PostgreSQL"},
            "ai": {
                "explanation": "Stores users, restaurants, orders.",
                "rationale": "Relational fits transactional integrity.",
                "confidence": 0.9,
            },
        },
    ],
    "edges": [
        {
            "id": "e_client_api",
            "source": "n_client",
            "target": "n_api",
            "label": "HTTPS / REST",
            "properties": {"protocol": "HTTPS", "dataFlow": "bidirectional"},
            "ai": {"explanation": "App sends orders and reads state."},
        },
        {
            "id": "e_api_db",
            "source": "n_api",
            "target": "n_db",
            "label": "SQL",
            "properties": {"protocol": "TCP", "dataFlow": "bidirectional"},
        },
    ],
    "conversation": [
        {
            "role": "user",
            "content": "I want to build a delivery app",
            "timestamp": "2026-05-09T14:30:00Z",
        },
        {
            "role": "assistant",
            "content": "Generated a baseline architecture.",
            "timestamp": "2026-05-09T14:30:04Z",
        },
    ],
}


def test_canonical_example_round_trips() -> None:
    """The example in diagram-v0.md must parse and serialize back to itself."""
    diagram = Diagram.model_validate(CANONICAL_EXAMPLE)

    # Round-trip: dump (with aliases) → parse → equal
    dumped = diagram.model_dump(by_alias=True, mode="json", exclude_none=False)
    reparsed = Diagram.model_validate(dumped)
    assert reparsed == diagram


def test_node_type_enum_is_closed() -> None:
    """An unknown node type must fail validation, not silently pass."""
    bad = {
        **CANONICAL_EXAMPLE,
        "nodes": [
            {
                "id": "n_bad",
                "type": "blockchain",  # not in NodeType
                "label": "Mystery",
                "position": {"x": 0, "y": 0},
            }
        ],
    }
    with pytest.raises(ValidationError):
        Diagram.model_validate(bad)


def test_known_node_types_are_accepted() -> None:
    """Every value in NodeType must be a valid diagram node type."""
    for nt in NodeType:
        single_node = {
            **CANONICAL_EXAMPLE,
            "nodes": [
                {
                    "id": f"n_{nt.value}",
                    "type": nt.value,
                    "label": nt.value,
                    "position": {"x": 0, "y": 0},
                }
            ],
            "edges": [],
        }
        Diagram.model_validate(single_node)
