
Penny MVP Implementation Plan
Step-by-step guide for Claude Code + Streamlit deployment
1. Purpose
This implementation plan translates the Penny MVP technical brief into a practical build sequence for Claude Code. The priority is a simple working demo with accurate calculations, low token usage, and safe budgeting/coaching advice.
2. Product Summary
Build a Streamlit app called Penny for young adults in Singapore.
Use simple preloaded Singapore transaction data instead of PDF bank statement extraction in the first version.
Show a spending dashboard, savings goal tracker, trade-off simulator, and Ask Penny chatbot.
Use SQLite so the demo can save user profile, transactions, goals, and summaries.
Use AI only on summarized financial context, not full transaction-level data.
Keep Penny focused on budgeting and behavioral coaching, not regulated financial advice.
3. How to Use This in Claude Code
Step
Action
Instruction
Step 1
Create a new project folder
Create a folder named penny_mvp and open it in Claude Code.
Step 2
Paste the technical brief first
Ask Claude Code to read the technical brief and confirm the app architecture before writing code.
Step 3
Paste this implementation plan
Ask Claude Code to follow the build phases below exactly and pause after each phase.
Step 4
Build in small increments
Do not ask for the entire app in one prompt. Build one phase at a time to reduce errors.
Step 5
Test after each phase
Run streamlit locally after each phase and fix errors before moving to the next step.
Step 6
Polish only at the end
Focus first on functionality and accuracy, then improve visuals once the app works.
4. Build Phases
Phase 0: Project Setup
Create the file structure: app.py, database.py, sample_data.py, categorizer.py, insights.py, tradeoff.py, ai_coach.py, requirements.txt, README.md.
Install core libraries: streamlit, pandas, plotly, python-dotenv.
Create a .env.example file for optional API keys.
Make sure the app can run with mock mode even without an API key.
Phase 1: Streamlit UI Skeleton
Create sidebar navigation with five pages: Profile, Dashboard, Goals, Trade-Off Simulator, Ask Penny.
Add a clean title and short product disclaimer.
Use session_state to maintain demo user context across pages.
Phase 2: SQLite Database
Build database.py with functions to initialize tables: users, transactions, goals, monthly_summaries.
Add insert/update/get helper functions.
Ensure the app creates penny.db automatically on first run.
Phase 3: Sample Singapore Transaction Data
Build sample_data.py with realistic SGD transactions across 2-3 months.
Include merchants such as Grab, SimplyGo, FairPrice, Shopee, Toast Box, Starbucks, Netflix, Spotify, Uniqlo, PayNow, DBS PayLah.
Load sample data into SQLite only once per demo user to avoid duplicates.
Phase 4: Categorization
Build categorizer.py with rule-based keyword mapping.
Categories should include Food & Drinks, Groceries, Transport, Shopping, Entertainment, Subscriptions, Travel, Education, Health, Income, Transfers, Other.
Keep categorization deterministic; do not use AI for this first version.
Phase 5: Dashboard and Insights
Build insights.py to calculate total income, expenses, net savings, top categories, top merchants, recurring subscriptions, largest transactions, and monthly trends.
Display metrics and charts in Streamlit.
Add short plain-English insights generated from calculations, not AI.
Phase 6: Savings Goal Tracker
Allow user to input goal name, target amount, current saved amount, and deadline.
Calculate progress percentage, remaining gap, monthly savings required, and whether the user is on track.
Save goals to SQLite.
Phase 7: Trade-Off Simulator
Build tradeoff.py to estimate the impact of a desired purchase on the savings goal.
Show estimated delay and possible offset actions, e.g. reduce Food & Drinks by SGD 20 per week.
Keep calculations simple, transparent, and explainable.
Phase 8: Ask Penny Chat
Build ai_coach.py with provider selection: Anthropic, OpenAI, or Mock Mode.
Use summarized context only: user profile, goal, total income/expenses, net savings, top categories, top merchants, recurring items, and user question.
Do not send all transactions to the model.
Include safety guardrails and a disclaimer in every chat session.
Phase 9: Coaching Styles
Add Penny, Mark, Van, and Fred as different tone presets.
Keep all styles safe and non-judgmental.
Do not let personalities change the financial logic; only change wording and tone.
Phase 10: Demo Polish and README
Improve layout, labels, and sample questions.
Add a README with setup instructions, how to run Streamlit, future PDF upload enhancement, and limitations.
Prepare a short demo script for class presentation.
5. Recommended Claude Code Prompts
Prompt 1: Architecture confirmation
Read the technical brief and this implementation plan. Before writing code, summarize the architecture, file structure, database schema, and build phases. Flag any issue that would make the app hard to deploy in Streamlit.
Prompt 2: Phase-by-phase execution
Build Phase 0 and Phase 1 only. Create the Streamlit UI skeleton, requirements.txt, and README starter. Do not build the database yet. After coding, tell me exactly how to run and test it.
Prompt 3: Database and sample data
Now build Phase 2 and Phase 3. Add SQLite database initialization and realistic Singapore sample transaction data. Ensure sample data loads once and avoids duplicate rows.
Prompt 4: Dashboard and calculations
Now build Phase 4 and Phase 5. Add rule-based categorization and dashboard insights. Prioritize calculation accuracy and clear visualizations.
Prompt 5: Goals and trade-offs
Now build Phase 6 and Phase 7. Add the savings goal tracker and trade-off simulator with transparent calculations and simple user-friendly explanations.
Prompt 6: Ask Penny chat
Now build Phase 8 and Phase 9. Add Ask Penny chat with summarized financial context only. Include mock mode so the app works without an API key. Keep responses safe, budgeting-focused, and non-regulated.
Prompt 7: Final polish
Review the full app for bugs, simplify the UI, update README, and add a short class demo script. Do not add new complex features.
6. Testing Checklist
App launches with streamlit run app.py.
Demo profile can be created without real login.
Sample data loads and does not duplicate after refresh.
Dashboard totals reconcile: income minus expenses equals net savings.
Categories look reasonable for Singapore merchants.
Savings goal calculations are accurate.
Trade-off simulator explains how the delay is calculated.
Ask Penny works in mock mode without API key.
Ask Penny does not provide investment, lending, crypto, insurance, or regulated product advice.
The app only sends summarized context to the AI provider.
README includes setup, run instructions, limitations, and future PDF upload enhancement.
7. Key Risks and Mitigations
Risk
Mitigation
AI cost / token usage
Send only compact financial summaries; default to mock mode when no API key is available.
Regulatory risk
Position Penny as budgeting and behavioral coaching only; avoid investment, credit, insurance, and product recommendations.
Demo reliability
Use sample data for the first version; list PDF bank statement upload as a future enhancement.
Inaccurate categorization
Use transparent rule-based categories and allow future manual edits.
Privacy concerns
Use local SQLite only for demo; do not upload transaction-level data to the AI provider.
8. Future Enhancements
PDF bank statement upload and extraction.
Manual transaction editing and export.
Real authentication.
Bank API integration.
Gamification, streaks, and rewards.
Family plan or parent dashboard.
Vendor partnerships with local merchants.
9. Final Instruction for Claude Code
Build a simple, stable, demo-ready version first. Do not over-engineer. Prioritize accuracy, clean UX, low token usage, and safe budgeting advice. Treat PDF extraction, real bank integrations, and advanced gamification as later versions.
