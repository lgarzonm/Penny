# 🐷 Penny

Penny is an AI-powered **budgeting and behavioral coaching** companion for young
adults in Singapore, built with [Streamlit](https://streamlit.io/). It helps
users understand their spending, set savings goals, simulate trade-offs, and
chat with a friendly coach for everyday money decisions.

> ⚠️ Penny is **not** an investment advisor, lending platform, crypto tool, or
> regulated financial advisor. It only provides budgeting, spending awareness,
> savings habits, and behavioral coaching.

## Features (MVP)

- **Profile** — quick setup, no real login required
- **Spending Dashboard** — YTD totals, spend by category/month, most-visited merchants, recurring subscriptions, lively insights
- **Goals** — progress tracking, monthly savings required, on-track status, tailored tips, and a **wishlist** of future purchases scored against your goal
- **Coach** — one chat that answers budgeting questions *and* runs purchase trade-offs, with four tone presets (Penny, Mark, Van, Fred)

Penny uses **preloaded Singapore sample data**, **rule-based categorization**
(no AI), and sends only **compact summaries** to the AI model. It runs in
**mock mode** with no API key.

## Project structure

```
app.py           Streamlit entry point — Profile, Dashboard, Goals, Coach
database.py      SQLite persistence (users, transactions, goals, summaries, wishlist)
sample_data.py   Preloaded Singapore sample transactions (YTD, with fluctuation)
categorizer.py   Rule-based categorization
insights.py      Dashboard metrics, goal progress, tips, AI context summary
tradeoff.py      Purchase trade-off calculations
ai_coach.py      Coach providers (Anthropic/OpenAI/Mock) + personalities
requirements.txt
docs/            Extracted technical brief & implementation plan
```

## Getting started

```bash
# 1. (optional) create a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. (optional) configure AI keys — defaults to mock mode without them
cp .env.example .env

# 4. run the app
streamlit run app.py
```

The SQLite database (`penny.db`) is created automatically on first run.

## AI providers

Penny supports Anthropic, OpenAI, or a key-free **mock mode**. Configure via
`.env` (see `.env.example`). Mock mode generates rule-based responses so the
demo works without paid API access.

## Demo script (class presentation)

A ~3-minute walkthrough:

1. **Intro (15s)** — "Penny is a budgeting coach for young adults in Singapore.
   It's coaching only — not investment or regulated advice."
2. **Profile (30s)** — Create a profile (e.g. *Alex, 18–24, SGD 2,800/mo*,
   goal *Japan trip — SGD 2,000 by December*, style *Penny*). Sample data loads
   automatically.
3. **Dashboard (45s)** — Show totals and the ~19% savings rate. Point out the
   category donut (Food & Drinks leads), monthly trend, top merchants, recurring
   subscriptions (Netflix/Spotify/Disney+), and the plain-English insights.
4. **Goals (45s)** — Show progress toward the Japan trip, monthly amount needed
   vs. current pace, the on-track badge, and the tailored tips. Add an item to
   the **wishlist** and show the estimated goal delay; click *Plan with Penny*.
5. **Coach (60s)** — The wishlist item arrives as a chat trade-off. Then ask
   "Where did I overspend?" and "How can I reach my goal faster?". Switch
   coaching style (e.g. to *Mark*) to show the tone change. Ask "Should I invest
   in Bitcoin?" to demonstrate the safety guardrail.
6. **Wrap (15s)** — Note it runs offline in mock mode, sends only summaries to
   the AI, and that PDF bank-statement upload is a planned enhancement.

Tip: use the **🔄 New demo session** button in the sidebar to reset between runs.

## Build status

This repo is being built phase-by-phase per `docs/implementation_plan.md`.

- [x] Phase 0 — Project setup & file structure
- [x] Phase 1 — Streamlit UI skeleton
- [x] Phase 2 — SQLite database
- [x] Phase 3 — Sample Singapore transaction data
- [x] Phase 4 — Categorization
- [x] Phase 5 — Dashboard & insights
- [x] Phase 6 — Savings goal tracker
- [x] Phase 7 — Trade-off simulator
- [x] Phase 8 — Ask Penny chat
- [x] Phase 9 — Coaching styles
- [x] Phase 10 — Polish & demo script

## Limitations

- Uses sample data, not real bank statements.
- No real authentication; demo profiles only.
- Coaching only — no investment, credit, crypto, insurance, or regulated advice.

## Future enhancements

- PDF bank statement upload and extraction
- Manual transaction editing and export
- Real authentication and bank API integration
- Gamification (streaks, rewards) and a family/parent dashboard

## Specs

The original product documents are preserved in [`docs/`](docs/):
- `docs/technical_brief.md` — Technical Brief: Penny MVP
- `docs/implementation_plan.md` — Penny MVP Implementation Plan
