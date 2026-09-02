"""inspect_diagram / inspect_node — the only chat tools."""

from __future__ import annotations

import json
from typing import Any

from app.schemas.diagram import Diagram

INSPECT_DIAGRAM = "inspect_diagram"
INSPECT_NODE = "inspect_node"

CHAT_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": INSPECT_DIAGRAM,
            "description": (
                "List every node (id, type, label) and every edge "
                "(id, source, target, label) on the current canvas. "
                "Call this before answering questions about the architecture "
                "as a whole. Do not invent nodes that are not returned."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": INSPECT_NODE,
            "description": (
                "Inspect one node by id: type, label, properties, and incident "
                "edges (what it connects to). When the user has a selected "
                "node, pass that id. Do not guess a node that is not returned."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "The node id to inspect.",
                    }
                },
                "required": ["node_id"],
                "additionalProperties": False,
            },
        },
    },
]


def inspect_diagram(diagram: Diagram | None) -> dict[str, Any]:
    if diagram is None:
        return {"error": "no_diagram"}
    return {
        "id": diagram.id,
        "name": diagram.metadata.name,
        "nodes": [{"id": n.id, "type": n.type.value, "label": n.label} for n in diagram.nodes],
        "edges": [
            {
                "id": e.id,
                "source": e.source,
                "target": e.target,
                "label": e.label,
            }
            for e in diagram.edges
        ],
    }


def inspect_node(diagram: Diagram | None, node_id: str | None) -> dict[str, Any]:
    if diagram is None:
        return {"error": "no_diagram"}
    if not node_id:
        return {"error": "unknown_node", "node_id": node_id}
    node = next((n for n in diagram.nodes if n.id == node_id), None)
    if node is None:
        return {"error": "unknown_node", "node_id": node_id}
    edges = [
        {
            "id": e.id,
            "source": e.source,
            "target": e.target,
            "label": e.label,
        }
        for e in diagram.edges
        if e.source == node_id or e.target == node_id
    ]
    return {
        "id": node.id,
        "type": node.type.value,
        "label": node.label,
        "properties": node.properties,
        "edges": edges,
    }


def execute_chat_tool(name: str, arguments: str, diagram: Diagram | None) -> dict[str, Any]:
    if name == INSPECT_DIAGRAM:
        return inspect_diagram(diagram)
    if name == INSPECT_NODE:
        try:
            args = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        node_id = args.get("node_id") if isinstance(args, dict) else None
        return inspect_node(diagram, node_id if isinstance(node_id, str) else None)
    return {"error": "unknown_tool", "name": name}
