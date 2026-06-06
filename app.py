"""Penny — AI financial decision coach for young adults in Singapore.

Streamlit entry point. This file wires up the navigation skeleton and shared
session state. Page logic is filled in across the build phases:

    Phase 1 (done): UI skeleton, sidebar nav, disclaimer, session state
    Phase 2 (done): SQLite database initialization
    Phase 3+:       sample data, dashboard, goals, trade-off, Ask Penny

Run with:  streamlit run app.py
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import database
import insights
import sample_data

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

PAGES = ["Profile", "Dashboard", "Goals", "Trade-Off Simulator", "Ask Penny"]


def init_session_state() -> None:
    """Ensure the keys we rely on across pages exist."""
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("profile", {})
    st.session_state.setdefault("chat_history", [])


def _placeholder(page: str, phase: str) -> None:
    st.subheader(page)
    st.info(f"🚧 Coming in a later build phase ({phase}).")


AGE_GROUPS = ["Under 18", "18-24", "25-34", "35-44", "45+"]


def render_profile() -> None:
    st.subheader("Demo Profile")
    st.caption("No real login required — this just sets up your demo session.")

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
                min_value=0.0,
                step=100.0,
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

        submitted = st.form_submit_button("Save profile & load demo data")

    if submitted:
        if not name.strip():
            st.error("Please enter a name.")
            return

        user_id = database.create_user(
            name=name.strip(),
            age_group=age_group,
            monthly_income=monthly_income,
            coaching_style=coaching_style,
        )
        database.upsert_goal(
            user_id,
            goal_name=goal_name.strip() or "My goal",
            target_amount=target_amount,
            current_amount=current_amount,
            deadline=target_date.isoformat(),
        )
        added = sample_data.load_sample_data(user_id, monthly_income)

        st.session_state["user_id"] = user_id
        st.session_state["profile"] = {
            "name": name.strip(),
            "age_group": age_group,
            "monthly_income": monthly_income,
            "coaching_style": coaching_style,
            "goal_name": goal_name.strip(),
            "target_amount": target_amount,
            "current_amount": current_amount,
        }
        st.success(
            f"Profile saved for {name.strip()}. Loaded {added} sample transactions. "
            "Head to the Dashboard next."
        )


def _require_user() -> int | None:
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("👈 Create a demo profile first (Profile page) to load your data.")
        return None
    return user_id


def render_dashboard() -> None:
    st.subheader("Spending Dashboard")
    user_id = _require_user()
    if not user_id:
        return

    transactions = database.get_transactions(user_id)
    ins = insights.compute_insights(transactions)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total income", f"SGD {ins['total_income']:,.2f}")
    c2.metric("Total expenses", f"SGD {ins['total_expenses']:,.2f}")
    c3.metric("Net savings", f"SGD {ins['net_savings']:,.2f}")
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
        st.markdown("**Income vs. expenses by month**")
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

    st.markdown("**Top merchants**")
    if ins["top_merchants"]:
        merch_df = pd.DataFrame(ins["top_merchants"]).sort_values("amount")
        fig = px.bar(merch_df, x="amount", y="merchant", orientation="h")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
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
    st.markdown("**💡 Insights**")
    for line in ins["text_insights"]:
        st.write(f"- {line}")


def render_goals() -> None:
    _placeholder("Savings Goal", "Phase 6")


def render_tradeoff() -> None:
    _placeholder("Trade-Off Simulator", "Phase 7")


def render_ask_penny() -> None:
    _placeholder("Ask Penny", "Phase 8")


PAGE_RENDERERS = {
    "Profile": render_profile,
    "Dashboard": render_dashboard,
    "Goals": render_goals,
    "Trade-Off Simulator": render_tradeoff,
    "Ask Penny": render_ask_penny,
}


def main() -> None:
    st.set_page_config(page_title="Penny", page_icon="🐷", layout="wide")
    database.init_db()
    init_session_state()

    st.title("🐷 Penny")
    st.caption("Your friendly budgeting & spending coach — built for Singapore.")
    st.warning(DISCLAIMER, icon="⚠️")

    with st.sidebar:
        st.header("Penny")
        page = st.radio("Navigate", PAGES, label_visibility="collapsed")
        st.divider()
        profile = st.session_state.get("profile") or {}
        if profile.get("name"):
            st.success(f"Demo user: {profile['name']}")
        else:
            st.caption("No demo profile yet — start on the Profile page.")

    PAGE_RENDERERS[page]()


if __name__ == "__main__":
    main()
