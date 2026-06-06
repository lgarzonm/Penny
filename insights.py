"""Spending insights and summaries (Phase 5).

All calculations are deterministic (no AI). Produces both the dashboard metrics
and the compact summary used by the AI coach (token minimization — never the
full transaction list).
"""

from __future__ import annotations

import pandas as pd


def _empty_insights() -> dict:
    return {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "net_savings": 0.0,
        "savings_rate": 0.0,
        "by_category": [],
        "by_month": [],
        "top_merchants": [],
        "largest_transactions": [],
        "recurring_subscriptions": [],
        "text_insights": ["No transactions yet — set up a profile to load demo data."],
    }


def compute_insights(transactions: list[dict]) -> dict:
    """Return dashboard metrics derived from a user's transactions."""
    if not transactions:
        return _empty_insights()

    df = pd.DataFrame(transactions)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["month"] = df["date"].str.slice(0, 7)

    expenses = df[df["type"] == "expense"]
    income = df[df["type"] == "income"]

    total_income = float(income["amount"].sum())
    total_expenses = float(expenses["amount"].sum())
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income else 0.0

    # Spending by category (descending).
    by_category = [
        {"category": cat, "amount": round(float(amt), 2)}
        for cat, amt in expenses.groupby("category")["amount"].sum().sort_values(ascending=False).items()
    ]

    # Income / expenses / net per month (chronological).
    by_month = []
    for month in sorted(df["month"].unique()):
        m = df[df["month"] == month]
        m_inc = float(m[m["type"] == "income"]["amount"].sum())
        m_exp = float(m[m["type"] == "expense"]["amount"].sum())
        by_month.append({
            "month": month,
            "income": round(m_inc, 2),
            "expenses": round(m_exp, 2),
            "net": round(m_inc - m_exp, 2),
        })

    # Top merchants by total spend.
    merchant_grp = expenses.groupby("merchant")["amount"].agg(["sum", "count"]).sort_values("sum", ascending=False)
    top_merchants = [
        {"merchant": merchant, "amount": round(float(row["sum"]), 2), "count": int(row["count"])}
        for merchant, row in merchant_grp.head(5).iterrows()
    ]

    # Largest single transactions.
    largest_transactions = [
        {
            "date": r["date"],
            "merchant": r["merchant"],
            "amount": round(float(r["amount"]), 2),
            "category": r["category"],
        }
        for _, r in expenses.sort_values("amount", ascending=False).head(5).iterrows()
    ]

    # Recurring subscriptions: Subscriptions-category merchants seen in 2+ months.
    subs = expenses[expenses["category"] == "Subscriptions"]
    recurring_subscriptions = []
    if not subs.empty:
        sub_grp = subs.groupby("merchant").agg(
            amount=("amount", "mean"), months=("month", "nunique")
        )
        for merchant, row in sub_grp.iterrows():
            if int(row["months"]) >= 2:
                recurring_subscriptions.append({
                    "merchant": merchant,
                    "amount": round(float(row["amount"]), 2),
                    "months": int(row["months"]),
                })

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_savings": round(net_savings, 2),
        "savings_rate": round(savings_rate, 1),
        "by_category": by_category,
        "by_month": by_month,
        "top_merchants": top_merchants,
        "largest_transactions": largest_transactions,
        "recurring_subscriptions": recurring_subscriptions,
        "text_insights": _text_insights(
            net_savings, savings_rate, by_category, recurring_subscriptions, largest_transactions
        ),
    }


def _text_insights(net_savings, savings_rate, by_category, recurring, largest) -> list[str]:
    """Generate short plain-English insights from the calculations."""
    out: list[str] = []

    if net_savings >= 0:
        out.append(f"You saved SGD {net_savings:,.2f} overall — a {savings_rate:.0f}% savings rate. Nice work. 🎉")
    else:
        out.append(f"You spent SGD {abs(net_savings):,.2f} more than you earned. Let's tighten things up. 💡")

    if by_category:
        top = by_category[0]
        out.append(f"Your biggest spending category is {top['category']} at SGD {top['amount']:,.2f}.")

    if recurring:
        total_subs = sum(r["amount"] for r in recurring)
        names = ", ".join(r["merchant"] for r in recurring)
        out.append(f"Recurring subscriptions ({names}) cost about SGD {total_subs:,.2f} per month.")

    if largest:
        big = largest[0]
        out.append(f"Your largest single purchase was SGD {big['amount']:,.2f} at {big['merchant']}.")

    return out


def build_ai_summary(profile: dict, transactions: list[dict], goal: dict | None) -> dict:
    """Build the compact financial summary sent to the AI coach.

    Deliberately small: profile + headline numbers + top-5 lists only.
    """
    ins = compute_insights(transactions)

    savings_gap = None
    if goal:
        target = float(goal.get("target_amount", 0) or 0)
        current = float(goal.get("current_amount", 0) or 0)
        savings_gap = round(target - current, 2)

    largest_spike = ins["largest_transactions"][0] if ins["largest_transactions"] else None

    return {
        "profile": {
            "name": (profile or {}).get("name"),
            "monthly_income": (profile or {}).get("monthly_income"),
            "coaching_style": (profile or {}).get("coaching_style"),
        },
        "goal": {
            "name": (goal or {}).get("goal_name"),
            "target_amount": (goal or {}).get("target_amount"),
            "current_amount": (goal or {}).get("current_amount"),
            "deadline": (goal or {}).get("deadline"),
            "savings_gap": savings_gap,
        } if goal else None,
        "financials": {
            "total_income": ins["total_income"],
            "total_expenses": ins["total_expenses"],
            "net_savings": ins["net_savings"],
            "savings_rate": ins["savings_rate"],
            "top_categories": ins["by_category"][:5],
            "top_merchants": ins["top_merchants"][:5],
            "recurring_subscriptions": ins["recurring_subscriptions"],
            "largest_spike": largest_spike,
        },
    }
