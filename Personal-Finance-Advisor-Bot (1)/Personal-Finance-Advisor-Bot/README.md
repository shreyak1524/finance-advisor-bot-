# Personal Finance Advisor Bot

A full-stack personal finance management web application built with **Python (Flask)**, **SQLite/MySQL**, and **vanilla JavaScript + Bootstrap 5**. Track income and expenses, set budgets, define savings goals, view monthly reports, and get AI-powered (or rule-based) financial recommendations — all in a clean, responsive dashboard.

---

## Features

- **User accounts** — register, log in, log out (passwords securely hashed)
- **Income tracking** — multiple entries per month, ideal for freelancers with variable income
- **Expense tracking** — categorized, with payment method, search and filters
- **Budgeting** — set a monthly budget per category, see spent/remaining/usage, get overspending warnings
- **Generate My Budget** — automatically suggests a budget based on your income and past spending (or a sensible 50/30/20 split if you're new)
- **Financial goals** — track progress toward savings targets with progress bars
- **Monthly reports** — category breakdown, budget performance, income variability, natural-language summary
- **AI Financial Advisor** — ask free-form questions about your finances
  - Uses an AI API (OpenAI or Gemini) if you provide a key
  - Automatically falls back to a built-in **rule-based recommendation engine** if no key is configured — the app always works
- **Demo data** — one click to populate your account with realistic sample data
- **Responsive design** — works on desktop, tablet and mobile

---

## Technology Stack

**Backend:** Python, Flask, Flask-SQLAlchemy, Flask-CORS, python-dotenv
**Database:** SQLite by default (zero setup), swappable to MySQL via an environment variable
**Frontend:** HTML5, CSS3, vanilla JavaScript, Bootstrap 5 (CDN), Font Awesome icons, Chart.js
**AI:** Pluggable AI service (OpenAI / Gemini) with automatic rule-based fallback

---

## Folder Structure

```
Personal-Finance-Advisor-Bot/
│
├── app.py                     # Application entry point
├── config.py                  # Environment-based configuration
├── constants.py                # Shared category/source lists
├── decorators.py              # login_required + current-user helper
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── models/
│   ├── __init__.py             # SQLAlchemy db instance
│   ├── user.py
│   ├── income.py
│   ├── expense.py
│   ├── budget.py
│   └── goal.py
│
├── routes/
│   ├── auth.py                 # register / login / logout / demo data
│   ├── dashboard.py
│   ├── income.py
│   ├── expenses.py
│   ├── budget.py
│   ├── goals.py
│   ├── reports.py
│   └── ai_advisor.py
│
├── services/
│   ├── ai_service.py            # calls OpenAI/Gemini if configured
│   ├── finance_service.py       # core calculations (totals, budgets, summaries)
│   └── recommendation_service.py # rule-based fallback recommendations
│
├── templates/                   # Jinja2 HTML templates
├── static/css/style.css
├── static/js/                   # one JS file per page + common.js helpers
└── instance/finance.db          # SQLite database (created automatically)
```

---

## Installation & Setup (Windows + VS Code)

### Step 1 — Open the project in VS Code
Extract the ZIP and open the `Personal-Finance-Advisor-Bot` folder in VS Code (`File > Open Folder...`).

### Step 2 — Create a virtual environment
Open a terminal in VS Code (`` Ctrl+` ``) and run:
```
python -m venv venv
```

### Step 3 — Activate the virtual environment
```
venv\Scripts\activate
```
You should see `(venv)` appear at the start of your terminal prompt.

### Step 4 — Install dependencies
```
pip install -r requirements.txt
```

### Step 5 — Create your `.env` file
Copy `.env.example` to a new file named `.env` in the project root:
```
copy .env.example .env
```
Open `.env` and set a `SECRET_KEY` (any random string). Leave `AI_API_KEY` empty unless you have one (see the AI section below).

### Step 6 — Database initialization
**No manual step needed.** The app automatically creates `instance/finance.db` (SQLite) and all required tables the first time it runs, via `db.create_all()` in `app.py`.

### Step 7 — Run the application
```
python app.py
```
or, alternatively:
```
python -m flask --app app run
```

### Step 8 — Open the app
Go to: **http://127.0.0.1:5000**

Register a new account, then optionally click **"Load Demo Data"** in the sidebar to explore the app with realistic sample numbers.

---

## Accessing from Your Phone (Same Wi-Fi)

1. Make sure your computer and phone are on the **same Wi-Fi network**.
2. Run the server so it listens on all network interfaces:
   ```
   python app.py
   ```
   (the app already runs with `host="0.0.0.0"` by default, so this works out of the box), or explicitly:
   ```
   flask --app app run --host=0.0.0.0 --port=5000
   ```
3. Find your computer's local IP address:
   ```
   ipconfig
   ```
   Look for the `IPv4 Address` under your active adapter (e.g. `192.168.1.42`).
4. On your phone's browser, open:
   ```
   http://192.168.1.42:5000
   ```
5. **Windows Firewall:** the first time you run the app, Windows may show a firewall prompt — click **"Allow access"** for both Private and Public networks so other devices can reach it. If you don't see a prompt and the phone can't connect, go to *Windows Defender Firewall > Allow an app through firewall* and make sure Python is allowed.

---

## AI Configuration (Optional)

The app works fully without any AI key, using a built-in rule-based recommendation engine (see `services/recommendation_service.py`).

To enable real AI-generated responses on the **AI Financial Advisor** page:

1. Open `.env`
2. Set:
   ```
   AI_PROVIDER=openai
   AI_API_KEY=your_openai_api_key_here
   ```
   or
   ```
   AI_PROVIDER=gemini
   AI_API_KEY=your_gemini_api_key_here
   ```
3. Restart the app (`python app.py`).

If the API key is missing, invalid, or the request fails for any reason (no internet, rate limit, etc.), the app **automatically and silently falls back** to the rule-based engine — the advisor page always returns a useful answer either way.

**Note:** Never commit your real API key. `.env` is already excluded via `.gitignore`.

---

## Switching to MySQL (Optional)

By default the app uses SQLite (`DATABASE_URL=sqlite:///finance.db`), which needs no setup.

To use MySQL instead:
1. Create a database in MySQL, e.g. `finance_db`.
2. In `.env`, set:
   ```
   DATABASE_URL=mysql+pymysql://username:password@localhost/finance_db
   ```
3. Restart the app — tables will be created automatically on first run.

---

## Demo Data

After registering, click **"Load Demo Data"** in the sidebar. This adds:
- 3 months of income (salary + occasional freelance income)
- A full month of categorized expenses
- A matching monthly budget
- Two sample financial goals (Emergency Fund, New Laptop)

This is entirely optional — the app works fine with an empty account too; just start adding your own income and expenses.

---

## Common Errors & Solutions

| Problem | Solution |
|---|---|
| `'python' is not recognized` | Install Python from python.org and make sure "Add to PATH" is checked during install. |
| `pip install` fails / SSL errors | Make sure you're connected to the internet and the virtual environment is activated (`venv\Scripts\activate`). |
| `ModuleNotFoundError: No module named 'flask'` | You forgot to activate the virtual environment, or `pip install -r requirements.txt` wasn't run. |
| Port 5000 already in use | Close other apps using port 5000, or run `flask --app app run --port=5001` and open that port instead. |
| Phone can't reach the app | Check both devices are on the same Wi-Fi, confirm the IP with `ipconfig`, and allow Python through Windows Firewall. |
| Database looks empty after restart | Make sure you're running the app from the same folder each time — SQLite's file lives at `instance/finance.db` relative to the project. |
| AI Advisor gives generic answers | This is expected without an API key — it's using the rule-based fallback. Add `AI_API_KEY` in `.env` to enable full AI responses. |

---

## Security Notes

- Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`) — plain text passwords are never stored.
- All financial data is scoped to `session["user_id"]` — one user can never see another user's income, expenses, budgets or goals.
- `.env` (containing secrets) is excluded from version control via `.gitignore`.
- API routes validate all input (amounts, dates, required fields) and return friendly JSON error messages instead of stack traces.

---

Enjoy managing your finances! 💰
