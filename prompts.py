"""Prompt templates for the VC decision memo agent."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a venture analyst. Use ONLY the provided context. "
    "If insufficient, reply exactly: \"Not enough evidence.\" "
    "Score each pillar 0–5 from evidence present. Return concise JSON only."
)

USER_TEMPLATE = (
    "Startup: {name}\n"
    "Investor constraints: stage={stage}, check_size={check_size}, horizon={horizon}\n\n"
    "Context (numbered, cite as [1], [2]…):\n{context}\n\n"
    "Return JSON keys:\n"
    "- verdict: \"Consider\" | \"Watchlist\" | \"Pass\"\n"
    "- scores: {team, problem, market, moat, traction, gtm, unit_economics, risks}\n"
    "- pros: [2-3 bullets with [#] citations]\n"
    "- cons: [2-3 bullets with [#] citations]\n"
    "- key_metrics: [1-3 items]\n"
    "- biggest_risks: [1-2 bullets]\n"
    "- fit_for_profile: \"1-2 sentences referencing stage/check_size\"\n"
    "- disclaimer: short non-advisory note"
)


def format_user_prompt(
    name: str,
    stage: str,
    check_size: str,
    horizon: str,
    context: str,
) -> str:
    """Format the user prompt given parameters and retrieved context."""
    return USER_TEMPLATE.format(
        name=name,
        stage=stage,
        check_size=check_size,
        horizon=horizon,
        context=context,
    )
