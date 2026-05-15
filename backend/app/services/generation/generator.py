"""Orchestrates the generate flow: prompt → LLM → validated Diagram."""

from __future__ import annotations

from datetime import UTC, datetime

from ulid import ULID

from app.schemas.diagram import Diagram, DiagramMetadata, Edge, EdgeAI, EdgeProperties
from app.schemas.generate import GeneratedDiagramContent
from app.services.generation.layout import auto_layout
from app.services.llm import LLMInvalidResponse, get_llm
from app.services.prompts import compose_prompt


async def generate_diagram(prompt: str) -> Diagram:
    """Generate a complete Diagram from a free-text prompt.

    Returns a fully-populated Diagram with backend-owned id, timestamps, and
    positions assigned by auto_layout. Raises LLMError subclasses on failure.
    """
    messages = await compose_prompt(prompt)
    llm = get_llm()
    content = await llm.generate_structured(messages, GeneratedDiagramContent)

    _validate_edge_integrity(content)

    now = datetime.now(UTC)
    positioned_nodes = auto_layout(content.nodes)

    edges = [_translate_edge(e) for e in content.edges]

    return Diagram(
        version="0.1.0",
        id=str(ULID()),
        metadata=DiagramMetadata.model_validate(
            {
                "name": content.name,
                "description": content.description,
                "createdAt": now,
                "updatedAt": now,
            }
        ),
        nodes=positioned_nodes,
        edges=edges,
        conversation=[],
    )


def _validate_edge_integrity(content: GeneratedDiagramContent) -> None:
    """Raise LLMInvalidResponse if any edge references a missing node id."""
    node_ids = {n.id for n in content.nodes}
    duplicates = _duplicates(n.id for n in content.nodes)
    if duplicates:
        raise LLMInvalidResponse(f"LLM produced duplicate node ids: {sorted(duplicates)}")
    for edge in content.edges:
        if edge.source not in node_ids:
            raise LLMInvalidResponse(
                f"Edge {edge.id!r} references unknown source node {edge.source!r}"
            )
        if edge.target not in node_ids:
            raise LLMInvalidResponse(
                f"Edge {edge.id!r} references unknown target node {edge.target!r}"
            )


def _duplicates(items) -> set[str]:  # noqa: ANN001
    seen: set[str] = set()
    dup: set[str] = set()
    for it in items:
        if it in seen:
            dup.add(it)
        seen.add(it)
    return dup


def _translate_edge(gen_edge) -> Edge:  # noqa: ANN001
    """Translate a GeneratedEdge to the canonical Edge shape."""
    return Edge(
        id=gen_edge.id,
        source=gen_edge.source,
        target=gen_edge.target,
        label=gen_edge.label,
        properties=EdgeProperties(
            protocol=gen_edge.properties.protocol,
            data_flow=gen_edge.properties.data_flow,
        ),
        ai=EdgeAI(explanation=gen_edge.ai.explanation) if gen_edge.ai else None,
    )
