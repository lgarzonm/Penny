# 🐷 Penny

Penny is an AI-powered **budgeting and behavioral coaching** companion for young
adults in Singapore, built with [Streamlit](https://streamlit.io/). It helps
users understand their spending, set savings goals, simulate trade-offs, and
chat with a friendly coach for everyday money decisions.

> ⚠️ Penny is **not** an investment advisor, lending platform, crypto tool, or
> regulated financial advisor. It only provides budgeting, spending awareness,
> savings habits, and behavioral coaching.

## Features (MVP)

- **Demo Profile** — quick setup, no real login required
- **Spending Dashboard** — totals, spend by category/month, top merchants, recurring subscriptions, insights
- **Savings Goal** — progress tracking, monthly savings required, on-track status
- **Trade-Off Simulator** — see how a purchase delays your goal and how to offset it
- **Ask Penny** — chat coach with four tone presets (Penny, Mark, Van, Fred)

Penny uses **preloaded Singapore sample data**, **rule-based categorization**
(no AI), and sends only **compact summaries** to the AI model. It runs in
**mock mode** with no API key.

## Project structure

```
app.py           Streamlit entry point + navigation skeleton
database.py      SQLite persistence (users, transactions, goals, summaries)
sample_data.py   Preloaded Singapore sample transactions   (Phase 3)
categorizer.py   Rule-based categorization                 (Phase 4)
insights.py      Dashboard metrics + AI context summary     (Phase 5)
tradeoff.py      Trade-off simulator                        (Phase 7)
ai_coach.py      Ask Penny providers (Anthropic/OpenAI/Mock) (Phases 8-9)
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

## Build status

This repo is being built phase-by-phase per `docs/implementation_plan.md`.

- [x] Phase 0 — Project setup & file structure
- [x] Phase 1 — Streamlit UI skeleton
- [x] Phase 2 — SQLite database
- [x] Phase 3 — Sample Singapore transaction data
- [x] Phase 4 — Categorization
- [x] Phase 5 — Dashboard & insights
- [x] Phase 6 — Savings goal tracker
- [ ] Phase 7 — Trade-off simulator
- [ ] Phase 8 — Ask Penny chat
- [ ] Phase 9 — Coaching styles
- [ ] Phase 10 — Polish & demo script

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
