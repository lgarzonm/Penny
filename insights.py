"""Spending insights and summaries (Phase 5).

Calculates total income, expenses, net savings, spend by category/month, top
merchants, largest transactions, recurring subscriptions, and plain-English
insights — all from deterministic calculations, not AI. Also produces the
compact summary used by the AI coach (token minimization).

Not implemented yet — placeholder for the next build phase.
"""

from __future__ import annotations


def compute_insights(transactions: list[dict]) -> dict:
    """Return dashboard metrics derived from a user's transactions."""
    raise NotImplementedError("Phase 5: dashboard insights")


def build_ai_summary(profile: dict, transactions: list[dict], goal: dict | None) -> dict:
    """Build the compact financial summary sent to the AI coach."""
    raise NotImplementedError("Phase 5: AI context summary")
