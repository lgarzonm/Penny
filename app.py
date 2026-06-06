"""Penny — AI financial decision coach for young adults in Singapore.

Streamlit entry point. This file wires up the navigation skeleton and shared
session state. Page logic is filled in across the build phases:

    Phase 1 (done): UI skeleton, sidebar nav, disclaimer, session state
    Phase 2 (done): SQLite database initialization
    Phase 3+:       sample data, dashboard, goals, trade-off, Ask Penny

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

import database

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


def render_profile() -> None:
    _placeholder("Demo Profile", "Phase 1 polish / wiring")
    st.caption(
        "Will collect: name, age group, monthly income (SGD), savings goal, "
        "target amount, target date, and preferred coaching style."
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
