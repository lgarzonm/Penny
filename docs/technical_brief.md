Technical Brief: Penny MVP — AI Financial Decision

Coach

Build a Streamlit web app called Penny, an AI-powered financial companion for young adults in Singapore.

Product Goal

Penny helps users understand their spending behavior, visualize trade-offs, and make smarter day-to-day

financial decisions.

Penny is not an investment advisor, lending platform, crypto tool, or regulated financial advisor. The app

should only provide budgeting, spending awareness, savings habits, and behavioral coaching.

MVP Scope

For the first version, use simple preloaded Singapore sample transaction data instead of PDF bank

statement extraction.

PDF bank statement upload can be included in the README as a future enhancement, but do not build it in
this version.

Core User Flow

1. 

User enters a simple demo profile.

2. 

App loads sample Singapore transaction data.

3. 

User sees spending dashboard.

4. 

User sets a savings goal.

5. 

User uses a trade-off simulator.

6. 

User chats with Penny for budgeting and spending advice.

App Pages

1. Demo Profile

No real login or password required.

Fields:

• 

Name

• 

Age group

• 

Monthly income / allowance in SGD

• 

Main savings goal

• 

Target amount

1

• 

Target date

• 

Preferred coaching style

Coaching styles:

• 

Penny: friendly and balanced

• 

Mark: direct and disciplined

• 

Van: balanced and compromise-driven

• 

Fred: wise and reflective

2. Spending Dashboard

Use preloaded realistic Singapore transaction data.

Sample merchants:

• 

Grab

• 

SimplyGo

• 

FairPrice

• 

Cold Storage

• 

Shopee

• 

Lazada

• 

Toast Box

• 

Starbucks

• 

Netflix

• 

Spotify

• 

Uniqlo

• 

PayNow Transfer

• 

DBS PayLah

Show:

• 

Total income

• 

Total expenses

• 

Net savings

• 

Spending by category

• 

Spending by month

• 

Top merchants

• 

Largest transactions

• 

Recurring subscriptions

• 

Simple spending insights

3. Savings Goal

Allow the user to input:

• 

Goal name

• 

Target amount

2

• 

Current saved amount

• 

Deadline

Show:

• 

Progress toward goal

• 

Monthly savings required

• 

Whether the user is on track based on current spending/savings behavior

4. Trade-Off Simulator

User enters:

• 

Desired purchase

• 

Purchase amount

• 

Category

App calculates:

• 

Impact on savings goal

• 

Estimated delay in reaching goal

• 

Possible spending trade-offs

Example output: “If you spend SGD 80 on this item, your Japan trip goal may be delayed by around 1.5

weeks unless you reduce food delivery by SGD 20 per week for the next month.”

5. Ask Penny Chat

A chatbot interface where users can ask:

• 

“Can I afford this?”

• 

“Where did I overspend this month?”

• 

“How can I save SGD 300 by August?”

• 

“What trade-off should I make if I buy this?”

The AI should use summarized financial context only, not the full transaction-level dataset.

Database

Use SQLite.

Suggested tables:

users

• 

user_id

• 

name

• 

age_group

3

• 

monthly_income

• 

coaching_style

• 

created_at

transactions

• 

transaction_id

• 

user_id

• 

date

• 

description

• 

merchant

• 

amount

• 

type: income / expense

• 

category

• 

created_at

goals

• 

goal_id

• 

user_id

• 

goal_name

• 

target_amount

• 

current_amount

• 

deadline

• 

created_at

monthly_summaries

• 

summary_id

• 

user_id

• 

month

• 

total_income

• 

total_expenses

• 

net_savings

• 

top_categories_json

• 

top_merchants_json

• 

recurring_items_json

• 

generated_at

Categorization

Use rule-based categorization to keep the app simple and reduce AI/token usage.

Categories:

• 

Food & Drinks

• 

Groceries

• 

Transport

4

• 

Shopping

• 

Entertainment

• 

Subscriptions

• 

Travel

• 

Education

• 

Health

• 

Income

• 

Transfers

• 

Other

Example rules:

• 

Grab, Gojek, SimplyGo, MRT → Transport

• 

FairPrice, Cold Storage, Giant → Groceries

• 

Netflix, Spotify, Disney, HBO → Subscriptions

• 

Shopee, Lazada, Uniqlo, Zara → Shopping

• 

Starbucks, Toast Box, McDonald’s, Kopitiam → Food & Drinks

• 

PayNow, PayLah → Transfers

Token Minimization

Do not send full transactions to the AI.

Only send a compact summary:

User profile:

• 

Monthly income

• 

Coaching style

• 

Savings goal

• 

Goal amount

• 

Deadline

Financial summary:

• 

Total income

• 

Total expenses

• 

Net savings

• 

Top 5 spending categories

• 

Top 5 merchants

• 

Recurring subscriptions

• 

Largest spending spike

• 

Savings gap vs target

User question:

• 

Latest chat message

5

AI Provider

Build flexible support for:

• 

Anthropic API if available

• 

OpenAI API if available

• 

Mock mode if no API key is available

Mock mode should generate basic rule-based responses so the demo works without paid API access.

AI Safety Rules

Penny should:

• 

Give budgeting and spending habit coaching.

• 

Explain trade-offs clearly.

• 

Use a balanced, slightly fun Gen Z tone.

• 

Avoid judgment or shame.

• 

Avoid investment advice.

• 

Avoid lending or credit product advice.

• 

Avoid crypto advice.

• 

Avoid insurance or regulated financial product recommendations.

• 

Avoid guarantees.

Include this disclaimer in the chat: “I’m not a licensed financial advisor. I can help with budgeting, spending

habits, and trade-offs, but not regulated financial or investment advice.”

Suggested File Structure

• 

app.py

• 

database.py

• 

sample_data.py

• 

categorizer.py

• 

insights.py

• 

tradeoff.py

• 

ai_coach.py

• 

requirements.txt

• 

README.md

Build Priority

1. 

Streamlit UI skeleton

2. 

SQLite database

3. 

sample Singapore transaction data

4. 

spending dashboard

5. 

savings goal page

6. 

trade-off simulator

6

7. 

Ask Penny chat using summarized data

8. 

coaching personalities

9. 

visual polish

10. 

README with future PDF upload enhancement

Success Criteria

The demo is successful if a user can: 1. Create a simple profile. 2. View realistic spending insights. 3. Set a

savings goal. 4. Simulate a trade-off. 5. Ask Penny a financial decision question. 6. Receive useful, safe,

personalized budgeting guidance.

7

