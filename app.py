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

import streamlit as st

import database
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


def render_dashboard() -> None:
    _placeholder("Spending Dashboard", "Phase 5")


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
