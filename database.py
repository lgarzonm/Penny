"""SQLite persistence layer for Penny.

Creates and manages the demo database (``penny.db`` by default) with four
tables: users, transactions, goals, and monthly_summaries. All access goes
through small helper functions so the rest of the app never writes raw SQL.

The database file is created automatically on first use.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Iterable, Optional

DB_PATH = os.environ.get("PENNY_DB_PATH", "penny.db")


# --------------------------------------------------------------------------- #
# Connection / schema
# --------------------------------------------------------------------------- #
def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Create all tables if they do not already exist (idempotent)."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT NOT NULL,
                age_group      TEXT,
                monthly_income REAL DEFAULT 0,
                coaching_style TEXT DEFAULT 'Penny',
                created_at     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                date           TEXT NOT NULL,
                description    TEXT,
                merchant       TEXT,
                amount         REAL NOT NULL,
                type           TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category       TEXT,
                created_at     TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS goals (
                goal_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                goal_name      TEXT NOT NULL,
                target_amount  REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline       TEXT,
                created_at     TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE TABLE IF NOT EXISTS monthly_summaries (
                summary_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id             INTEGER NOT NULL,
                month               TEXT NOT NULL,
                total_income        REAL DEFAULT 0,
                total_expenses      REAL DEFAULT 0,
                net_savings         REAL DEFAULT 0,
                top_categories_json TEXT,
                top_merchants_json  TEXT,
                recurring_items_json TEXT,
                generated_at        TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );

            CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions (user_id);
            CREATE INDEX IF NOT EXISTS idx_goal_user ON goals (user_id);
            CREATE INDEX IF NOT EXISTS idx_summary_user ON monthly_summaries (user_id);
            """
        )


def _now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
def create_user(
    name: str,
    age_group: str = "",
    monthly_income: float = 0.0,
    coaching_style: str = "Penny",
) -> int:
    """Insert a user and return the new user_id."""
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO users (name, age_group, monthly_income, coaching_style, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (name, age_group, monthly_income, coaching_style, _now()),
        )
        return int(cur.lastrowid)


def update_user(user_id: int, **fields: Any) -> None:
    """Update allowed user fields by keyword (name, age_group, ...)."""
    allowed = {"name", "age_group", "monthly_income", "coaching_style"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    cols = ", ".join(f"{k} = ?" for k in updates)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE users SET {cols} WHERE user_id = ?",
            (*updates.values(), user_id),
        )


def get_user(user_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_name(name: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE name = ? ORDER BY user_id LIMIT 1", (name,)
        ).fetchone()
        return dict(row) if row else None


# --------------------------------------------------------------------------- #
# Transactions
# --------------------------------------------------------------------------- #
def insert_transaction(
    user_id: int,
    date: str,
    amount: float,
    type: str,
    description: str = "",
    merchant: str = "",
    category: str = "Other",
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO transactions
               (user_id, date, description, merchant, amount, type, category, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, date, description, merchant, amount, type, category, _now()),
        )
        return int(cur.lastrowid)


def insert_transactions(rows: Iterable[dict]) -> int:
    """Bulk insert. Each row is a dict matching insert_transaction kwargs
    (plus user_id). Returns the number of rows inserted."""
    payload = [
        (
            r["user_id"],
            r["date"],
            r.get("description", ""),
            r.get("merchant", ""),
            r["amount"],
            r["type"],
            r.get("category", "Other"),
            _now(),
        )
        for r in rows
    ]
    if not payload:
        return 0
    with get_connection() as conn:
        conn.executemany(
            """INSERT INTO transactions
               (user_id, date, description, merchant, amount, type, category, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            payload,
        )
    return len(payload)


def get_transactions(user_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY date", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def count_transactions(user_id: int) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM transactions WHERE user_id = ?", (user_id,)
        ).fetchone()
        return int(row["n"])


# --------------------------------------------------------------------------- #
# Goals
# --------------------------------------------------------------------------- #
def upsert_goal(
    user_id: int,
    goal_name: str,
    target_amount: float,
    current_amount: float = 0.0,
    deadline: str = "",
) -> int:
    """Create or update the user's goal (single goal per user for the MVP)."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT goal_id FROM goals WHERE user_id = ? ORDER BY goal_id LIMIT 1",
            (user_id,),
        ).fetchone()
        if existing:
            conn.execute(
                """UPDATE goals
                   SET goal_name = ?, target_amount = ?, current_amount = ?, deadline = ?
                   WHERE goal_id = ?""",
                (goal_name, target_amount, current_amount, deadline, existing["goal_id"]),
            )
            return int(existing["goal_id"])
        cur = conn.execute(
            """INSERT INTO goals
               (user_id, goal_name, target_amount, current_amount, deadline, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, goal_name, target_amount, current_amount, deadline, _now()),
        )
        return int(cur.lastrowid)


def get_goal(user_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM goals WHERE user_id = ? ORDER BY goal_id LIMIT 1", (user_id,)
        ).fetchone()
        return dict(row) if row else None


# --------------------------------------------------------------------------- #
# Monthly summaries
# --------------------------------------------------------------------------- #
def save_monthly_summary(user_id: int, month: str, summary: dict) -> None:
    """Insert or replace a cached monthly summary. JSON fields are serialized."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM monthly_summaries WHERE user_id = ? AND month = ?",
            (user_id, month),
        )
        conn.execute(
            """INSERT INTO monthly_summaries
               (user_id, month, total_income, total_expenses, net_savings,
                top_categories_json, top_merchants_json, recurring_items_json, generated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                month,
                summary.get("total_income", 0),
                summary.get("total_expenses", 0),
                summary.get("net_savings", 0),
                json.dumps(summary.get("top_categories", [])),
                json.dumps(summary.get("top_merchants", [])),
                json.dumps(summary.get("recurring_items", [])),
                _now(),
            ),
        )


def get_monthly_summaries(user_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM monthly_summaries WHERE user_id = ? ORDER BY month",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print(f"Initialized database at {DB_PATH}")
