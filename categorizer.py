"""Rule-based transaction categorization (Phase 4).

Deterministic keyword mapping (no AI) into: Food & Drinks, Groceries,
Transport, Shopping, Entertainment, Subscriptions, Travel, Education, Health,
Income, Transfers, Other.

Not implemented yet — placeholder for the next build phase.
"""

from __future__ import annotations


def categorize(description: str, merchant: str = "") -> str:
    """Return a category for a transaction using keyword rules."""
    raise NotImplementedError("Phase 4: rule-based categorization")
