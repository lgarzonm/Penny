"""Ask Penny AI coach (Phases 8-9).

Provider selection (Anthropic, OpenAI, or Mock mode) with summarized financial
context only — never full transaction-level data. Includes safety guardrails
(no investment/credit/crypto/insurance advice), a disclaimer, and tone presets
for the Penny, Mark, Van, and Fred coaching styles.

Mock mode returns rule-based responses so the demo works without an API key.

Not implemented yet — placeholder for the next build phase.
"""

from __future__ import annotations

DISCLAIMER = (
    "I'm not a licensed financial advisor. I can help with budgeting, spending "
    "habits, and trade-offs, but not regulated financial or investment advice."
)


def ask_penny(question: str, summary: dict, coaching_style: str = "Penny") -> str:
    """Answer a user question using the compact financial summary."""
    raise NotImplementedError("Phase 8: Ask Penny chat")
