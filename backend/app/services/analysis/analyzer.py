"""Orchestrates the analyze flow: diagram → findings + prose feedback.

Two independent products come out of one diagram:

- `findings` — the deterministic output of the rules engine. The source of
  truth for *what* is wrong. Reproducible, model-free, testable in isolation.
- `feedback` — the tutor's prose *around* those findings, from the LLM.

The composer already injects the diagram and the findings into the system
prompt (see `compose_prompt` / `_findings_block_safe`), so the LLM sees the
same findings we return. We deliberately call the rules engine here too,
rather than thread pre-computed findings through the composer: the checks are
pure and cheap, and keeping the composer's interface unchanged is worth one
extra graph pass.
"""

from __future__ import annotations

from app.schemas.analyze import AnalyzeResponse
from app.schemas.diagram import Diagram
from app.services.llm import get_llm
from app.services.prompts import compose_prompt
from app.services.rules import check_all

# `/analyze` has no free-text user request — the request is implicitly
# "review this diagram." The composer appends the serialized diagram to the
# user message; this is the instruction that precedes it.
_REVIEW_INSTRUCTION = (
    "Review the following architecture diagram. Explain any structural issues, "
    "referring to the static-analysis findings where relevant, and suggest how "
    "to improve it. If it looks sound, say what it does well."
)


async def analyze_diagram(diagram: Diagram, mode_id: str = "tutor") -> AnalyzeResponse:
    """Analyze a diagram: deterministic findings plus LLM prose feedback.

    Returns both products. Raises ModeNotFoundError for an unknown mode_id and
    LLMError subclasses if the feedback call fails — the caller (the router)
    maps those to HTTP statuses.
    """
    findings = check_all(diagram)

    messages = await compose_prompt(_REVIEW_INSTRUCTION, diagram=diagram, mode_id=mode_id)
    llm = get_llm()
    feedback = await llm.generate(messages)

    return AnalyzeResponse(findings=findings, feedback=feedback)
