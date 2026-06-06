"""Penny — AI financial decision coach for young adults in Singapore.

Streamlit entry point. Pages: Profile, Dashboard, Goals, and Coach (a merged
chat that answers budgeting questions and runs purchase trade-offs).

Run with:  streamlit run app.py
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import ai_coach
import database
import insights
import sample_data
import tradeoff
from categorizer import CATEGORIES

DISCLAIMER = (
    "I'm not a licensed financial advisor. I can help with budgeting, spending "
    "habits, and trade-offs, but not regulated financial or investment advice."
)

COACHING_STYLES = {
    "Penny": "friendly and balanced",
    "Mark": "direct and disciplined",
    "Van": "balanced and compromise-driven",
    "Fred": "wise and reflective",
}

PAGES = ["Profile", "Dashboard", "Goals", "Coach"]
AGE_GROUPS = ["Under 18", "18-24", "25-34", "35-44", "45+"]
SPEND_CATEGORIES = [c for c in CATEGORIES if c not in ("Income", "Transfers")]


def init_session_state() -> None:
    """Ensure the keys we rely on across pages exist."""
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("profile", {})
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("nav", "Profile")
    st.session_state.setdefault("pending_purchase", None)


# --------------------------------------------------------------------------- #
# Navigation callbacks (safe to mutate widget state inside on_click)
# --------------------------------------------------------------------------- #
def _goto(page: str) -> None:
    st.session_state["nav"] = page


def _goto_purchase(item: dict) -> None:
    st.session_state["pending_purchase"] = item
    st.session_state["nav"] = "Coach"


def _reset_session() -> None:
    st.session_state["user_id"] = None
    st.session_state["profile"] = {}
    st.session_state["chat_history"] = []
    st.session_state["pending_purchase"] = None
    st.session_state["nav"] = "Profile"


def _require_user() -> int | None:
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("👈 Create a demo profile first (Profile page) to load your data.")
        return None
    return user_id


# --------------------------------------------------------------------------- #
# Profile
# --------------------------------------------------------------------------- #
def render_profile() -> None:
    st.subheader("Your Profile")

    with st.expander("👋 New here? How Penny works", expanded=False):
        st.markdown(
            "1. **Profile** — set up your details and goal.\n"
            "2. **Dashboard** — see where your money goes.\n"
            "3. **Goals** — track progress and save future wishes.\n"
            "4. **Coach** — chat with Penny and test purchases before you buy."
        )

    st.caption("Tell Penny a little about yourself, then scroll down to save.")
    existing = st.session_state.get("profile") or {}

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=existing.get("name", ""))
            age_group = st.selectbox(
                "Age group",
                AGE_GROUPS,
                index=AGE_GROUPS.index(existing.get("age_group", "18-24"))
                if existing.get("age_group") in AGE_GROUPS
                else 1,
            )
            monthly_income = st.number_input(
                "Monthly income / allowance (SGD)",
                min_value=0.0, step=100.0,
                value=float(existing.get("monthly_income", 2500.0)),
            )
            coaching_style = st.selectbox(
                "Preferred coaching style",
                list(COACHING_STYLES),
                index=list(COACHING_STYLES).index(existing.get("coaching_style", "Penny")),
                format_func=lambda s: f"{s} — {COACHING_STYLES[s]}",
            )
        with col2:
            goal_name = st.text_input(
                "Main savings goal", value=existing.get("goal_name", "Japan trip")
            )
            target_amount = st.number_input(
                "Target amount (SGD)", min_value=0.0, step=100.0,
                value=float(existing.get("target_amount", 2000.0)),
            )
            current_amount = st.number_input(
                "Current saved amount (SGD)", min_value=0.0, step=50.0,
                value=float(existing.get("current_amount", 0.0)),
            )
            target_date = st.date_input("Target date", value=date.today())

        submitted = st.form_submit_button(
            "Save profile", type="primary", use_container_width=True
        )

    if submitted:
        if not name.strip():
            st.error("Please enter a name.")
            return

        user_id = database.create_user(
            name=name.strip(), age_group=age_group,
            monthly_income=monthly_income, coaching_style=coaching_style,
        )
        database.upsert_goal(
            user_id,
            goal_name=goal_name.strip() or "My goal",
            target_amount=target_amount,
            current_amount=current_amount,
            deadline=target_date.isoformat(),
        )
        sample_data.load_sample_data(user_id, monthly_income)

        st.session_state["user_id"] = user_id
        st.session_state["profile"] = {
            "name": name.strip(), "age_group": age_group,
            "monthly_income": monthly_income, "coaching_style": coaching_style,
            "goal_name": goal_name.strip(), "target_amount": target_amount,
            "current_amount": current_amount,
        }

    if st.session_state.get("user_id"):
        st.markdown("**You're all set!** Your financial overview is ready. 🎉")
        st.button(
            "Head to the Dashboard →", type="primary",
            on_click=_goto, args=("Dashboard",),
        )


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
def render_dashboard() -> None:
    st.subheader("Spending Dashboard")
    user_id = _require_user()
    if not user_id:
        return

    ins = insights.compute_insights(database.get_transactions(user_id))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total income", f"SGD {ins['total_income']:,.0f}")
    c2.metric("Total expenses", f"SGD {ins['total_expenses']:,.0f}")
    c3.metric("Net savings", f"SGD {ins['net_savings']:,.0f}")
    c4.metric("Savings rate", f"{ins['savings_rate']:.0f}%")

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("**Spending by category**")
        if ins["by_category"]:
            cat_df = pd.DataFrame(ins["by_category"])
            fig = px.pie(cat_df, names="category", values="amount", hole=0.45)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No expense data.")

    with right:
        st.markdown("**Income vs. expenses by month (2026 YTD)**")
        if ins["by_month"]:
            month_df = pd.DataFrame(ins["by_month"])
            melted = month_df.melt(
                id_vars="month", value_vars=["income", "expenses"],
                var_name="type", value_name="amount",
            )
            fig = px.bar(melted, x="month", y="amount", color="type", barmode="group")
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No monthly data.")

    st.markdown("**🏪 Most visited merchants**")
    if ins["frequent_merchants"]:
        fm = pd.DataFrame(ins["frequent_merchants"]).sort_values("count")
        fig = px.bar(
            fm, x="count", y="merchant", orientation="h",
            labels={"count": "visits", "merchant": ""},
            hover_data={"amount": ":.0f"},
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Largest transactions**")
        if ins["largest_transactions"]:
            st.dataframe(
                pd.DataFrame(ins["largest_transactions"]),
                hide_index=True, use_container_width=True,
            )
    with col_b:
        st.markdown("**Recurring subscriptions**")
        if ins["recurring_subscriptions"]:
            st.dataframe(
                pd.DataFrame(ins["recurring_subscriptions"]),
                hide_index=True, use_container_width=True,
            )
        else:
            st.caption("No recurring subscriptions detected.")

    st.divider()
    st.markdown("#### 💡 Penny's read on your money")
    for line in ins["text_insights"]:
        st.markdown(f"##### {line}")


# --------------------------------------------------------------------------- #
# Goals
# --------------------------------------------------------------------------- #
def render_goals() -> None:
    st.subheader("Savings Goal")
    user_id = _require_user()
    if not user_id:
        return

    goal = database.get_goal(user_id) or {}

    with st.form("goal_form"):
        col1, col2 = st.columns(2)
        with col1:
            goal_name = st.text_input("Goal name", value=goal.get("goal_name", "My goal"))
            target_amount = st.number_input(
                "Target amount (SGD)", min_value=0.0, step=100.0,
                value=float(goal.get("target_amount", 2000.0) or 0.0),
            )
        with col2:
            current_amount = st.number_input(
                "Current saved amount (SGD)", min_value=0.0, step=50.0,
                value=float(goal.get("current_amount", 0.0) or 0.0),
            )
            deadline_default = date.fromisoformat(goal["deadline"]) if goal.get("deadline") else date.today()
            deadline = st.date_input("Deadline", value=deadline_default)
        saved = st.form_submit_button("Save goal", type="primary", use_container_width=True)

    if saved:
        database.upsert_goal(
            user_id, goal_name=goal_name.strip() or "My goal",
            target_amount=target_amount, current_amount=current_amount,
            deadline=deadline.isoformat(),
        )
        prof = st.session_state.get("profile") or {}
        prof.update({
            "goal_name": goal_name.strip(), "target_amount": target_amount,
            "current_amount": current_amount,
        })
        st.session_state["profile"] = prof
        goal = database.get_goal(user_id) or {}

    if not goal:
        st.info("Set a goal above to see your progress.")
        return

    ins = insights.compute_insights(database.get_transactions(user_id))
    prog = insights.compute_goal_progress(goal, ins)

    st.divider()
    st.markdown(f"### {goal.get('goal_name', 'My goal')}")
    st.progress(
        min(prog["progress_pct"] / 100, 1.0),
        text=f"{prog['progress_pct']:.0f}% · SGD {prog['current_amount']:,.0f} of SGD {prog['target_amount']:,.0f}",
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Remaining", f"SGD {prog['remaining']:,.0f}")
    c2.metric("Monthly needed", f"SGD {prog['monthly_required']:,.0f}")
    c3.metric("Your pace / mo", f"SGD {prog['current_pace']:,.0f}")

    if prog["on_track"] is True:
        st.success("✅ You're on track to reach this goal at your current pace.")
    elif prog["on_track"] is False:
        st.warning("⚠️ At your current pace you may miss this goal. Try the tips below or ask Penny in the Coach tab.")

    if prog["projected_date"]:
        st.caption(
            f"At your current pace you'd reach the goal in ~{prog['projected_months']:.1f} "
            f"months (around {prog['projected_date']})."
        )

    # Preliminary advice
    st.markdown("#### 💡 Ways to reach your goal faster")
    for tip in insights.generate_goal_tips(ins, prog):
        st.write(tip)

    # Wishlist of future purchases
    _render_wishlist(user_id, ins, goal)


def _render_wishlist(user_id: int, ins: dict, goal: dict) -> None:
    st.divider()
    st.markdown("#### 🎁 Wishlist — things you're eyeing")
    st.caption("Save future purchases here and see how each one would affect this goal.")

    with st.form("wish_form", clear_on_submit=True):
        wc1, wc2, wc3 = st.columns([2, 1, 1])
        with wc1:
            item_name = st.text_input("Item", placeholder="e.g. AirPods Pro")
        with wc2:
            amount = st.number_input("Price (SGD)", min_value=0.0, step=10.0, value=100.0)
        with wc3:
            category = st.selectbox("Category", SPEND_CATEGORIES, index=SPEND_CATEGORIES.index("Shopping"))
        add = st.form_submit_button("➕ Add to wishlist", use_container_width=True)

    if add and item_name.strip():
        database.add_wish(user_id, item_name.strip(), amount, category)

    wishes = database.get_wishlist(user_id)
    if not wishes:
        st.caption("Your wishlist is empty. Add something you're dreaming about! ✨")
        return

    goal_name = goal.get("goal_name", "your goal")
    prog = insights.compute_goal_progress(goal, ins)
    for w in wishes:
        result = tradeoff.simulate(
            w["amount"], ins, goal_progress=prog,
            goal_name=goal_name, purchase_name=w["item_name"],
        )
        delay = result["delay_weeks"]
        delay_txt = f"~{delay:.1f} wk delay" if delay is not None else "impact unclear"
        r1, r2, r3 = st.columns([3, 1, 1])
        r1.markdown(f"**{w['item_name']}** · SGD {w['amount']:,.0f}  \n🕒 {delay_txt} to {goal_name}")
        r2.button(
            "💬 Plan with Penny", key=f"plan_{w['wish_id']}",
            on_click=_goto_purchase,
            args=({"item_name": w["item_name"], "amount": w["amount"], "category": w["category"]},),
        )
        r3.button("🗑️ Remove", key=f"del_{w['wish_id']}", on_click=database.delete_wish, args=(w["wish_id"],))


# --------------------------------------------------------------------------- #
# Coach (merged Ask Penny + Trade-Off)
# --------------------------------------------------------------------------- #
SAMPLE_QUESTIONS = [
    "Can I afford a SGD 120 concert ticket?",
    "Where did I overspend this month?",
    "How can I reach my savings goal faster?",
    "Which subscriptions should I cancel?",
]


def _push_purchase_to_chat(user_id, profile, ins, goal, purchase_name, amount, coaching_style):
    """Compute a trade-off and append it to the chat as a Q&A turn."""
    goal_name = (goal or {}).get("goal_name", "your goal")
    prog = insights.compute_goal_progress(goal, ins) if goal else None
    result = tradeoff.simulate(
        amount, ins, goal_progress=prog,
        goal_name=goal_name, purchase_name=purchase_name,
    )
    advice = ai_coach.format_purchase_advice(purchase_name, result, goal_name, coaching_style)
    history = st.session_state["chat_history"]
    history.append({"role": "user", "content": f"Can I afford {purchase_name} (SGD {amount:,.0f})?"})
    history.append({"role": "assistant", "content": advice})


def render_coach() -> None:
    st.subheader("Penny — your money coach 🪙")
    user_id = _require_user()
    if not user_id:
        return

    provider = ai_coach.get_active_provider()
    st.caption(ai_coach.DISCLAIMER)
    if provider == "mock":
        st.success(
            "Mock mode — no API usage. Responses are generated locally for free. "
            "Set a key in `.env` for live AI responses.",
            icon="🟢",
        )
    else:
        st.info(f"Live AI mode — using **{provider}** (this consumes API credits).", icon="🔵")

    profile = st.session_state.get("profile") or {}
    current_style = profile.get("coaching_style", "Penny")
    coaching_style = st.selectbox(
        "Coaching style",
        list(COACHING_STYLES),
        index=list(COACHING_STYLES).index(current_style) if current_style in COACHING_STYLES else 0,
        format_func=lambda s: f"{s} — {COACHING_STYLES[s]}",
        help="Changes Penny's tone only — the budgeting advice stays the same.",
    )
    if coaching_style != current_style:
        profile["coaching_style"] = coaching_style
        st.session_state["profile"] = profile
        database.update_user(user_id, coaching_style=coaching_style)

    transactions = database.get_transactions(user_id)
    goal = database.get_goal(user_id)
    ins = insights.compute_insights(transactions)
    summary = insights.build_ai_summary(profile, transactions, goal)
    history = st.session_state["chat_history"]

    # Handle a purchase sent over from the wishlist.
    pending = st.session_state.get("pending_purchase")
    if pending:
        _push_purchase_to_chat(
            user_id, profile, ins, goal,
            pending["item_name"], pending["amount"], coaching_style,
        )
        st.session_state["pending_purchase"] = None

    # Inline purchase tester.
    with st.expander("🛍️ Thinking about buying something? Test it"):
        with st.form("coach_purchase", clear_on_submit=True):
            pc1, pc2 = st.columns([2, 1])
            with pc1:
                p_name = st.text_input("What is it?", placeholder="e.g. New sneakers")
            with pc2:
                p_amount = st.number_input("Price (SGD)", min_value=0.0, step=10.0, value=80.0)
            ask = st.form_submit_button("Ask Penny about it", type="primary", use_container_width=True)
        if ask and p_name.strip():
            _push_purchase_to_chat(user_id, profile, ins, goal, p_name.strip(), p_amount, coaching_style)
            st.rerun()

    if not history:
        st.markdown("**Try asking:**")
        for q in SAMPLE_QUESTIONS:
            st.write(f"💬 {q}")

    for msg in history:
        with st.chat_message(msg["role"], avatar="🪙" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask Penny anything about your money…")
    if prompt:
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🪙"):
            with st.spinner("Penny is thinking…"):
                answer = ai_coach.ask_penny(prompt, summary, coaching_style, history[:-1])
            st.markdown(answer)
        history.append({"role": "assistant", "content": answer})


PAGE_RENDERERS = {
    "Profile": render_profile,
    "Dashboard": render_dashboard,
    "Goals": render_goals,
    "Coach": render_coach,
}


def main() -> None:
    st.set_page_config(page_title="Penny", page_icon="🪙", layout="wide")
    database.init_db()
    init_session_state()

    st.title("🪙 Penny")
    st.caption("Your friendly budgeting & spending coach — built for Singapore.")
    st.warning(DISCLAIMER, icon="⚠️")

    with st.sidebar:
        st.header("Penny")
        st.radio("Navigate", PAGES, label_visibility="collapsed", key="nav")
        st.divider()
        profile = st.session_state.get("profile") or {}
        if profile.get("name"):
            st.success(f"Demo user: {profile['name']}")
            st.caption(f"Coaching style: {profile.get('coaching_style', 'Penny')}")
        else:
            st.caption("No demo profile yet — start on the Profile page.")
        st.caption(f"AI provider: {ai_coach.get_active_provider()}")
        st.divider()
        st.button("🔄 New demo session", on_click=_reset_session)

    PAGE_RENDERERS[st.session_state["nav"]]()


if __name__ == "__main__":
    main()
