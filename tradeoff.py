"""Trade-off simulator (Phase 7).

Estimates how a desired purchase affects the user's savings goal and suggests
transparent offset actions. All math is simple and explainable:

    delay  = purchase_amount / monthly_savings_pace
    offset = spread the purchase over ~4 weeks by trimming a discretionary
             category (purchase_amount / 4 per week)
"""

from __future__ import annotations

import insights

_WEEKS_PER_MONTH = 4.345

# Categories a user can realistically cut back to offset a purchase.
_DISCRETIONARY = ("Food & Drinks", "Shopping", "Entertainment", "Subscriptions", "Travel")


def simulate(
    purchase_amount: float,
    insights_result: dict,
    goal_progress: dict | None = None,
    goal_name: str = "your goal",
    purchase_name: str = "this purchase",
) -> dict:
    """Return the estimated goal impact and suggested offsets for a purchase."""
    purchase_amount = max(float(purchase_amount or 0), 0.0)
    pace = insights.avg_monthly_savings(insights_result)

    if pace > 0:
        delay_months = round(purchase_amount / pace, 2)
        delay_weeks = round(delay_months * _WEEKS_PER_MONTH, 1)
    else:
        delay_months = None
        delay_weeks = None

    # Suggest offsets from the biggest discretionary categories.
    by_category = insights_result.get("by_category") or []
    discretionary = [c for c in by_category if c["category"] in _DISCRETIONARY]
    weekly = round(purchase_amount / 4, 2) if purchase_amount else 0.0
    offsets = [
        {
            "category": c["category"],
            "weekly_amount": weekly,
            "weeks": 4,
            "note": f"Trim {c['category']} by SGD {weekly:,.2f}/week for 4 weeks",
        }
        for c in discretionary[:2]
    ]

    message = _build_message(
        purchase_amount, purchase_name, goal_name, delay_weeks, offsets, pace, goal_progress
    )

    return {
        "purchase_amount": round(purchase_amount, 2),
        "pace": pace,
        "delay_months": delay_months,
        "delay_weeks": delay_weeks,
        "offsets": offsets,
        "message": message,
    }


def _build_message(
    amount, purchase_name, goal_name, delay_weeks, offsets, pace, goal_progress
) -> str:
    if amount <= 0:
        return "Enter a purchase amount to see the trade-off."

    if pace <= 0:
        return (
            f"You're not saving anything on average right now, so spending SGD {amount:,.2f} "
            f"on {purchase_name} would set back {goal_name} until you start saving."
        )

    parts = [
        f"If you spend SGD {amount:,.2f} on {purchase_name}, "
        f"{goal_name} may be delayed by around {delay_weeks:.1f} weeks"
    ]
    if offsets:
        o = offsets[0]
        parts.append(
            f" unless you {o['note'][0].lower() + o['note'][1:]}"
        )
    parts.append(".")

    msg = "".join(parts)

    # If the goal would slip past its deadline, flag it.
    if goal_progress and goal_progress.get("on_track") is True and goal_progress.get("months_left") is not None:
        slack = goal_progress["months_left"] - (goal_progress.get("projected_months") or 0)
        if delay_weeks and (delay_weeks / _WEEKS_PER_MONTH) > slack:
            msg += " ⚠️ This could push you past your deadline."
    return msg
