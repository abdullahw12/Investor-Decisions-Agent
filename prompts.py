"""Prompt templates for the VC decision memo agent."""
from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a venture analyst. Use ONLY the provided context to generate investment analysis. "
    "If insufficient information, reply exactly: \"Not enough evidence.\" "
    "Score each pillar 0–5 based on evidence present. "
    "You MUST return valid JSON format only, no additional text or explanations."
)

USER_TEMPLATE = (
    "Company: {name}\n"
    "Investment parameters: stage={stage}, check_size={check_size}, horizon={horizon}\n\n"
    "Context (numbered, cite as [1], [2]…):\n{context}\n\n"
    "Return ONLY valid JSON with these exact keys:\n"
    "{{\n"
    '  "verdict": "Consider" | "Watchlist" | "Pass",\n'
    '  "scores": {{\n'
    '    "team": 0-5,\n'
    '    "problem": 0-5,\n'
    '    "market": 0-5,\n'
    '    "moat": 0-5,\n'
    '    "traction": 0-5,\n'
    '    "gtm": 0-5,\n'
    '    "unit_economics": 0-5,\n'
    '    "risks": 0-5\n'
    '  }},\n'
    '  "pros": ["bullet 1 [1]", "bullet 2 [2]"],\n'
    '  "cons": ["bullet 1 [1]", "bullet 2 [2]"],\n'
    '  "key_metrics": ["metric 1", "metric 2"],\n'
    '  "biggest_risks": ["risk 1", "risk 2"],\n'
    '  "fit_for_profile": "1-2 sentences about fit",\n'
    '  "disclaimer": "This is not investment advice"\n'
    "}}"
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
