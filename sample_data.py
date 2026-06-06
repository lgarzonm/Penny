"""Preloaded Singapore sample transaction data (Phase 3).

Will generate ~2-3 months of realistic SGD transactions across merchants such
as Grab, SimplyGo, FairPrice, Cold Storage, Shopee, Lazada, Toast Box,
Starbucks, Netflix, Spotify, Uniqlo, PayNow Transfer, and DBS PayLah, and load
them into SQLite once per demo user (guarded against duplicates).

Not implemented yet — placeholder for the next build phase.
"""

from __future__ import annotations


def load_sample_data(user_id: int) -> int:
    """Load sample transactions for the user if none exist. Returns rows added."""
    raise NotImplementedError("Phase 3: sample Singapore transaction data")
