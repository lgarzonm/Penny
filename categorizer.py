"""Rule-based transaction categorization (Phase 4).

Deterministic keyword mapping (no AI) so categorization is fast, free, and
explainable. Matching is case-insensitive against the merchant and description.

Categories: Food & Drinks, Groceries, Transport, Shopping, Entertainment,
Subscriptions, Travel, Education, Health, Income, Transfers, Other.
"""

from __future__ import annotations

CATEGORIES = [
    "Food & Drinks",
    "Groceries",
    "Transport",
    "Shopping",
    "Entertainment",
    "Subscriptions",
    "Travel",
    "Education",
    "Health",
    "Income",
    "Transfers",
    "Other",
]

# Ordered rules: the first category with a matching keyword wins. Order matters
# where merchants could overlap (e.g. groceries before generic shopping).
_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Income", ("salary", "payroll", "allowance", "stipend", "refund", "cashback")),
    ("Groceries", ("fairprice", "cold storage", "giant", "sheng siong", "ntuc")),
    ("Transport", ("grab", "gojek", "simplygo", "mrt", "comfortdelgro", "tada", "bus", "ez-link")),
    ("Subscriptions", ("netflix", "spotify", "disney", "hbo", "youtube premium", "apple", "icloud", "amazon prime")),
    ("Shopping", ("shopee", "lazada", "uniqlo", "zara", "h&m", "qoo10", "decathlon", "ikea")),
    ("Food & Drinks", ("starbucks", "toast box", "mcdonald", "kopitiam", "kfc", "subway", "ya kun", "koi", "liho", "foodpanda", "deliveroo")),
    ("Entertainment", ("golden village", "cathay", "gv ", "shaw", "steam", "cinema", "klook")),
    ("Travel", ("airlines", "scoot", "airbnb", "hotel", "expedia", "agoda", "singapore air", "changi")),
    ("Education", ("course", "udemy", "coursera", "school", "tuition", "kinokuniya", "popular bookstore")),
    ("Health", ("clinic", "pharmacy", "guardian", "watsons", "hospital", "polyclinic", "gym", "anytime fitness")),
    ("Transfers", ("paynow", "paylah", "transfer", "fast payment")),
]


def categorize(description: str = "", merchant: str = "", txn_type: str = "expense") -> str:
    """Return a category for a transaction using keyword rules.

    ``txn_type`` of ``"income"`` short-circuits to the Income category so that
    salary/allowance entries are never misclassified as spending.
    """
    if txn_type == "income":
        return "Income"

    haystack = f"{merchant} {description}".lower()
    for category, keywords in _RULES:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "Other"
