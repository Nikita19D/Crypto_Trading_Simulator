# Crypto Trading Simulator

## IMPORTANT NOTICE (READ THIS FIRST)

> ## THIS PROJECT IS NOT LIVE RIGHT NOW
> The app used an AWS RDS MySQL database for user authentication and app data.
> That database was running on a free trial, and the free trial has ended.
> Because of that, login/registration and most data-driven features will not work until a new database is set up.

## What this project is

This is a desktop crypto trading simulator built in Python.

Simple version:
- You make an account.
- You get fake money ($10,000).
- You buy/sell crypto with fake money.
- You can check portfolio stats, leaderboard, and learning modules.

No real money is used.

## Main features

- Login + registration (passwords hashed with bcrypt)
- Trading dashboard
- Live-ish pricing from Bybit API
- Portfolio screen with summary + chart
- Leaderboard (users sorted by balance)
- Learning section (4 beginner-friendly modules)
- Basic test scripts in the `Testing/` folder

## Project structure (quick view)

- `login_screen.py` -> login UI
- `registration_screen.py` -> sign-up UI
- `trading_screen.py` -> main trading dashboard
- `portfolio.py` -> holdings, metrics, transaction history UI
- `leaderboard.py` -> top users by balance
- `learning.py` -> educational modules
- `db_connection.py` -> DB + trading logic + API calls
- `Database/MySQL/` -> MySQL scripts (schema, populate, tests, etc.)
- `Database/SQLite/` -> SQLite experiments/tests
- `Testing/` -> manual-style python test scripts

## Tech stack

- Python
- PySide6 (desktop UI)
- MySQL (original backend)
- requests (API calls)
- bcrypt (password hashing)
- pyqtgraph + matplotlib (charts)

## How to run (local)

1. Install dependencies:

```bash
pip install pyside6 mysql-connector-python requests bcrypt pyqtgraph matplotlib
```

2. Start the app:

```bash
python login_screen.py
```

## Current status

Right now, without replacing/reconnecting the database, expect DB-based flows to fail:
- registration
- login
- portfolio persistence
- leaderboard data
- transaction history

UI code is still here and can be run, but full app behavior needs a working DB.

## Tests

There is no formal pytest suite in this repo.
There are script-style tests in `Testing/` that print PASS/FAILED output.

Examples:

```bash
python Testing/db_connection_tests.py
python Testing/trading_tests.py
python Testing/portfolio_tests.py
python Testing/leaderboard_tests.py
python Testing/learning_tests.py
```

Most DB tests also require a working MySQL backend.

## Practical next step to revive project

If you want this live again, easiest path is:
- spin up a new MySQL instance (AWS, local Docker, or local install)
- recreate schema from scripts in `Database/MySQL/`
- update DB config in `db_connection.py`
- retest login + trading flow

---

Built as a simulation/learning project.
Not financial advice. Not connected to real trading accounts.
