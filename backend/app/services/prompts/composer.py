"""Compose the message list for any LLM call.

The composer is the single bridge between the curated knowledge (modes,
components, patterns), the static analysis (rules), and the LLM provider
interface. Every endpoint that talks to an LLM uses `compose_prompt`.
"""

from __future__ import annotations

import logging

from app.schemas.chat import ChatMessage
from app.schemas.diagram import Diagram
from app.schemas.finding import Finding
from app.services.components import load_components
from app.services.modes import get_mode
from app.services.retrieval import retrieve_patterns
from app.services.rules import check_all

logger = logging.getLogger(__name__)

_SECTION_SEPARATOR = "\n\n---\n\n"


async def compose_prompt(
    user_request: str,
    diagram: Diagram | None = None,
    mode_id: str = "tutor",
    k_patterns: int = 3,
) -> list[ChatMessage]:
    """Build the two-message list to send to the LLM.

    The first message is `system` and contains: the mode persona, a compact
    summary of every component type, top-k retrieved patterns relevant to the
    user request, and (if a diagram is supplied) the deterministic rule
    findings for that diagram.

    The second message is `user` and contains the request text plus the
    serialized diagram when one is supplied.

    Raises ModeNotFoundError if `mode_id` is unknown. Every other sub-system
    failure (retrieval down, rules raising) degrades gracefully — the section
    is omitted, a warning is logged, and composition continues.
    """
    sections: list[str] = []

    # 1. Mode persona — raises ModeNotFoundError on unknown id. Intentional:
    # an unknown mode is a programmer error, not a runtime issue we paper over.
    mode = get_mode(mode_id)
    sections.append(mode.system_prompt.strip())

    # 2. Component vocabulary — always included.
    vocabulary = _component_vocabulary_block_safe()
    if vocabulary:
        sections.append(vocabulary)

    # 3. Retrieved patterns — best effort.
    patterns_block = await _patterns_block_safe(user_request, k_patterns)
    if patterns_block:
        sections.append(patterns_block)

    # 4. Static analysis — only when a diagram was supplied.
    if diagram is not None:
        findings_block = _findings_block_safe(diagram)
        if findings_block:
            sections.append(findings_block)

    system_content = _SECTION_SEPARATOR.join(sections)
    user_content = _user_message_content(user_request, diagram)

    return [
        ChatMessage(role="system", content=system_content),
        ChatMessage(role="user", content=user_content),
    ]


# ---------------------------------------------------------------------------
# Section builders (each one catches its own exceptions and returns a string
# or None; the composer never crashes on a sub-system failure).
# ---------------------------------------------------------------------------


def _component_vocabulary_block_safe() -> str | None:
    try:
        components = load_components()
    except Exception as e:
        logger.warning("Component metadata unavailable for prompt composition: %s", e)
        return None

    lines = ["# Component vocabulary", ""]
    for node_type, component in sorted(components.items(), key=lambda kv: kv[0].value):
        lines.append(f"## {component.label} (`{node_type.value}`)")
        lines.append(component.description.strip())
        if component.tradeoffs:
            preview = component.tradeoffs[:2]
            lines.append("Key tradeoffs:")
            for t in preview:
                lines.append(f"- {t}")
        lines.append("")
    return "\n".join(lines).rstrip()


async def _patterns_block_safe(user_request: str, k: int) -> str | None:
    try:
        matches = await retrieve_patterns(user_request, k=k)
    except Exception as e:
        logger.warning("Pattern retrieval failed during prompt composition: %s", e)
        return None

    if not matches:
        # Retrieval returned empty (degraded); don't emit a section header.
        return None

    lines = ["# Relevant patterns", ""]
    for i, m in enumerate(matches, start=1):
        lines.append(f"## {i}. {m.pattern.title}  (id: `{m.pattern.id}`)")
        lines.append(m.pattern.body.strip())
        lines.append("")
    return "\n".join(lines).rstrip()


def _findings_block_safe(diagram: Diagram) -> str | None:
    try:
        findings = check_all(diagram)
    except Exception as e:
        logger.warning("Rules engine failed during prompt composition: %s", e)
        return None

    if not findings:
        return "# Static analysis findings\n\nNo structural issues detected by the rules engine."

    lines = ["# Static analysis findings", ""]
    lines.append(
        "Pre-LLM, deterministic. The user already sees these; "
        "refer to them explicitly when relevant."
    )
    lines.append("")
    for f in findings:
        lines.append(_format_finding(f))
    return "\n".join(lines).rstrip()


def _format_finding(finding: Finding) -> str:
    severity = finding.severity.value.upper()
    bits = [f"- **[{severity}]** {finding.message}", f"  (rule: `{finding.rule_id}`)"]
    if finding.node_ids:
        bits.append(f"  nodes: {', '.join(finding.node_ids)}")
    return "\n".join(bits)


def _user_message_content(user_request: str, diagram: Diagram | None) -> str:
    if diagram is None:
        return user_request
    diagram_json = diagram.model_dump_json(by_alias=True, indent=2)
    return f"{user_request}\n\nCurrent diagram (JSON):\n```json\n{diagram_json}\n```"
