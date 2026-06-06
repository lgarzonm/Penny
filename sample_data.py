"""Preloaded Singapore sample transaction data (Phase 3).

Generates ~3 months of realistic SGD transactions for a demo user across common
Singapore merchants, then loads them into SQLite. Generation is deterministic
per user (seeded by ``user_id``) and guarded so it only runs once per user.

Categories are assigned via :mod:`categorizer` so there is a single source of
truth for categorization.
"""

from __future__ import annotations

import calendar
import random
from datetime import date, timedelta

import categorizer
import database

DEFAULT_MONTHLY_INCOME = 2500.0

# (merchant, min_amount, max_amount) pools for expense generation.
_FOOD = [
    ("Toast Box", 3.0, 8.0),
    ("Starbucks", 6.0, 9.5),
    ("McDonald's", 8.0, 14.0),
    ("Kopitiam", 4.0, 9.0),
    ("Ya Kun Kaya Toast", 4.0, 9.0),
    ("KOI", 4.0, 7.0),
    ("Din Tai Fung", 22.0, 45.0),
    ("Genki Sushi", 18.0, 35.0),
    ("foodpanda", 15.0, 32.0),
]
_TRANSPORT = [
    ("Grab", 9.0, 26.0),
    ("SimplyGo", 1.4, 2.8),
    ("Gojek", 9.0, 24.0),
]
_GROCERIES = [
    ("FairPrice", 25.0, 90.0),
    ("Cold Storage", 30.0, 95.0),
    ("Giant", 20.0, 75.0),
]
_SHOPPING = [
    ("Shopee", 20.0, 130.0),
    ("Lazada", 25.0, 120.0),
    ("Uniqlo", 35.0, 150.0),
]
_TRANSFERS = [
    ("PayNow Transfer", 20.0, 80.0),
    ("DBS PayLah", 10.0, 45.0),
]
_ENTERTAINMENT = [
    ("Golden Village", 13.0, 17.0),
    ("Klook", 25.0, 70.0),
]
# Fixed monthly subscriptions (merchant, amount, day-of-month).
_SUBSCRIPTIONS = [
    ("Netflix", 17.98, 5),
    ("Spotify", 10.98, 12),
    ("Disney+", 11.98, 18),
]
# Fixed monthly bills (merchant, amount, day-of-month, category).
_BILLS = [
    ("Singtel", 42.90, 8, "Other"),
    ("Family Contribution (PayNow)", 300.0, 2, "Transfers"),
]


def _months_back(n: int) -> list[date]:
    """Return the first-of-month dates for the ``n`` full months before today,
    in chronological order."""
    first_of_this = date.today().replace(day=1)
    months: list[date] = []
    cursor = first_of_this
    for _ in range(n):
        cursor = (cursor - timedelta(days=1)).replace(day=1)
        months.append(cursor)
    return list(reversed(months))


def _rand_day(rng: random.Random, month_start: date) -> str:
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    day = rng.randint(1, last_day)
    return month_start.replace(day=day).isoformat()


def _expense(rng: random.Random, month_start: date, pool: list[tuple[str, float, float]]) -> dict:
    merchant, low, high = rng.choice(pool)
    amount = round(rng.uniform(low, high), 2)
    return {
        "date": _rand_day(rng, month_start),
        "description": merchant,
        "merchant": merchant,
        "amount": amount,
        "type": "expense",
        "category": categorizer.categorize(merchant=merchant, txn_type="expense"),
    }


def generate_transactions(user_id: int, monthly_income: float) -> list[dict]:
    """Build (but do not persist) the sample transaction list for a user."""
    rng = random.Random(user_id or 1)
    income = monthly_income if monthly_income and monthly_income > 0 else DEFAULT_MONTHLY_INCOME
    rows: list[dict] = []

    # Per-month volume of each expense type (realistic ~15-20% savings rate,
    # with Food & Drinks as the leading category — typical for Singapore).
    plan = [
        (_FOOD, 34),
        (_TRANSPORT, 24),
        (_GROCERIES, 6),
        (_SHOPPING, 7),
        (_TRANSFERS, 2),
        (_ENTERTAINMENT, 5),
    ]

    for month_start in _months_back(3):
        # Monthly income (salary / allowance) near the start of the month.
        rows.append({
            "date": month_start.replace(day=1).isoformat(),
            "description": "Monthly income",
            "merchant": "Salary / Allowance",
            "amount": round(income, 2),
            "type": "income",
            "category": "Income",
        })

        last_day = calendar.monthrange(month_start.year, month_start.month)[1]

        # Fixed monthly bills (rent, telco, family contribution).
        for merchant, amount, day, category in _BILLS:
            rows.append({
                "date": month_start.replace(day=min(day, last_day)).isoformat(),
                "description": merchant,
                "merchant": merchant,
                "amount": amount,
                "type": "expense",
                "category": category,
            })

        # Fixed recurring subscriptions (so the dashboard can detect them).
        for merchant, amount, day in _SUBSCRIPTIONS:
            rows.append({
                "date": month_start.replace(day=min(day, last_day)).isoformat(),
                "description": f"{merchant} subscription",
                "merchant": merchant,
                "amount": amount,
                "type": "expense",
                "category": categorizer.categorize(merchant=merchant, txn_type="expense"),
            })

        # Variable everyday spending.
        for pool, count in plan:
            for _ in range(count):
                rows.append(_expense(rng, month_start, pool))

    for row in rows:
        row["user_id"] = user_id

    rows.sort(key=lambda r: r["date"])
    return rows


def load_sample_data(user_id: int, monthly_income: float | None = None) -> int:
    """Load sample transactions for the user if they have none.

    Returns the number of rows inserted (0 if data already existed)."""
    if database.count_transactions(user_id) > 0:
        return 0

    if monthly_income is None:
        user = database.get_user(user_id)
        monthly_income = (user or {}).get("monthly_income", DEFAULT_MONTHLY_INCOME)

    rows = generate_transactions(user_id, monthly_income or DEFAULT_MONTHLY_INCOME)
    return database.insert_transactions(rows)
