"""Ask Penny AI coach (Phase 8, with style hooks for Phase 9).

Provider selection (Anthropic, OpenAI, or Mock) driven by environment
variables. Only a compact financial *summary* is ever sent to a model — never
the full transaction list (token minimization).

Safety: budgeting / spending / savings coaching only. Questions about
regulated topics (investing, credit, crypto, insurance, etc.) are redirected
locally without an API call. A disclaimer is shown in every chat session.
"""

from __future__ import annotations

import json
import os

DISCLAIMER = (
    "I'm not a licensed financial advisor. I can help with budgeting, spending "
    "habits, and trade-offs, but not regulated financial or investment advice."
)

# Tone presets (Phase 9). Logic never changes — only wording/voice.
COACHING_TONES = {
    "Penny": "friendly and balanced, with a warm, slightly fun Gen Z vibe",
    "Mark": "direct and disciplined, concise and no-nonsense but never harsh",
    "Van": "balanced and compromise-driven, weighing both sides fairly",
    "Fred": "wise and reflective, calm and thoughtful",
}

# Topics Penny must not advise on — redirected locally (no API call).
RESTRICTED_TOPICS = (
    "invest", "stock", "shares", "etf", "crypto", "bitcoin", "ethereum",
    "forex", "insurance", "mortgage", "loan", "borrow", "options trading",
    "interest rate", "gamble", "lottery", "fixed deposit", "bonds",
)


# --------------------------------------------------------------------------- #
# Provider resolution
# --------------------------------------------------------------------------- #
def get_active_provider() -> str:
    """Return the provider that will actually be used: anthropic | openai | mock."""
    pref = os.environ.get("PENNY_AI_PROVIDER", "mock").strip().lower()
    if pref == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if pref == "openai" and os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return "mock"


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def ask_penny(
    question: str,
    summary: dict,
    coaching_style: str = "Penny",
    history: list[dict] | None = None,
) -> str:
    """Answer a user question using the compact financial summary."""
    question = (question or "").strip()
    if not question:
        return "Ask me anything about your budgeting or spending! 💸"

    if _is_restricted(question):
        return _restricted_response(coaching_style)

    provider = get_active_provider()
    try:
        if provider == "anthropic":
            return _anthropic_response(question, summary, coaching_style, history)
        if provider == "openai":
            return _openai_response(question, summary, coaching_style, history)
    except Exception:
        # Any provider/network error falls back to the mock so the demo never breaks.
        pass
    return _mock_response(question, summary, coaching_style)


def _is_restricted(question: str) -> bool:
    q = question.lower()
    return any(topic in q for topic in RESTRICTED_TOPICS)


def _restricted_response(coaching_style: str) -> str:
    return (
        "That's a bit outside what I can help with — I stick to budgeting, "
        "spending habits, and savings, not investments, credit, crypto, or "
        f"insurance.\n\n{DISCLAIMER}"
    )


# --------------------------------------------------------------------------- #
# Prompt construction
# --------------------------------------------------------------------------- #
def _system_prompt(coaching_style: str) -> str:
    tone = COACHING_TONES.get(coaching_style, COACHING_TONES["Penny"])
    return (
        "You are Penny, a budgeting and behavioral money coach for a young adult "
        "in Singapore (amounts in SGD). "
        f"Your tone is {tone}. "
        "Help with budgeting, spending awareness, savings habits, and trade-offs. "
        "Be encouraging and non-judgmental — never shame the user. "
        "Do NOT give investment, lending/credit, crypto, or insurance advice, and "
        "never make guarantees. Keep answers short (2-4 sentences) and concrete, "
        "referencing the user's numbers when useful. "
        f"End with this disclaimer on its own line: \"{DISCLAIMER}\""
    )


def _format_summary(summary: dict) -> str:
    """Compact, human-readable rendering of the summary for the model."""
    return json.dumps(summary, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Real providers (lazy imports)
# --------------------------------------------------------------------------- #
def _anthropic_response(question, summary, coaching_style, history) -> str:
    import anthropic

    client = anthropic.Anthropic()
    model = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    messages = _history_messages(history)
    messages.append({
        "role": "user",
        "content": f"Financial summary:\n{_format_summary(summary)}\n\nQuestion: {question}",
    })
    resp = client.messages.create(
        model=model,
        max_tokens=400,
        system=_system_prompt(coaching_style),
        messages=messages,
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def _openai_response(question, summary, coaching_style, history) -> str:
    from openai import OpenAI

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    messages = [{"role": "system", "content": _system_prompt(coaching_style)}]
    messages.extend(_history_messages(history))
    messages.append({
        "role": "user",
        "content": f"Financial summary:\n{_format_summary(summary)}\n\nQuestion: {question}",
    })
    resp = client.chat.completions.create(model=model, max_tokens=400, messages=messages)
    return resp.choices[0].message.content.strip()


def _history_messages(history: list[dict] | None) -> list[dict]:
    """Keep only the last few turns to stay token-light."""
    if not history:
        return []
    trimmed = history[-6:]
    return [{"role": h["role"], "content": h["content"]} for h in trimmed]


# --------------------------------------------------------------------------- #
# Mock provider (no API key required)
# --------------------------------------------------------------------------- #
def _mock_response(question: str, summary: dict, coaching_style: str) -> str:
    q = question.lower()
    fin = (summary or {}).get("financials", {}) or {}
    goal = (summary or {}).get("goal") or {}

    net = fin.get("net_savings", 0)
    income = fin.get("total_income", 0)
    expenses = fin.get("total_expenses", 0)
    rate = fin.get("savings_rate", 0)
    top_cats = fin.get("top_categories") or []
    top_merchants = fin.get("top_merchants") or []
    recurring = fin.get("recurring_subscriptions") or []
    top_cat = top_cats[0]["category"] if top_cats else "your top category"
    top_cat_amt = top_cats[0]["amount"] if top_cats else 0

    if any(w in q for w in ("afford", "can i buy", "should i buy", "can i get")):
        body = (
            f"Over the last few months you've netted about SGD {net:,.0f} "
            f"(a {rate:.0f}% savings rate). If a purchase is small relative to that, "
            "you can likely absorb it — try the Trade-Off Simulator to see the exact "
            "impact on your goal first."
        )
    elif any(w in q for w in ("overspend", "where did", "spending most", "biggest")):
        body = f"Your biggest category is {top_cat} at about SGD {top_cat_amt:,.0f}."
        if top_merchants:
            m = top_merchants[0]
            body += f" Your top merchant is {m['merchant']} (~SGD {m['amount']:,.0f})."
    elif any(w in q for w in ("save", "saving", "goal", "reach")):
        gap = goal.get("savings_gap")
        if goal and gap is not None:
            body = (
                f"To hit your '{goal.get('name','goal')}' you still need about "
                f"SGD {gap:,.0f}. At your current pace of ~SGD {net/3:,.0f}/month "
                "you're making progress — trimming a discretionary category would speed it up."
            )
        else:
            body = (
                f"You're saving about SGD {net/3:,.0f}/month. Set a goal on the Goals "
                "page and I'll tell you exactly how much to put aside each month."
            )
    elif any(w in q for w in ("subscription", "recurring", "cancel")):
        if recurring:
            names = ", ".join(r["merchant"] for r in recurring)
            total = sum(r["amount"] for r in recurring)
            body = (
                f"Your recurring subscriptions are {names}, costing ~SGD {total:,.0f}/month. "
                "Cancelling one you barely use is an easy win."
            )
        else:
            body = "I don't see regular subscriptions in your data right now."
    else:
        body = (
            f"Here's a quick snapshot: income SGD {income:,.0f}, expenses "
            f"SGD {expenses:,.0f}, net savings SGD {net:,.0f} ({rate:.0f}%). "
            f"Your largest category is {top_cat}. Ask me about affording a purchase, "
            "where you overspend, or how to reach your goal."
        )

    return f"{_tone_prefix(coaching_style)}{body}\n\n{DISCLAIMER}"


def _tone_prefix(coaching_style: str) -> str:
    return {
        "Penny": "",
        "Mark": "Straight talk: ",
        "Van": "Let's weigh it up: ",
        "Fred": "Something to reflect on: ",
    }.get(coaching_style, "")
