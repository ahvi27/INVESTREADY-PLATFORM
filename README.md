# InvestReady — Investment Attraction Intelligence Platform

InvestReady is a polished Python decision-support application for investment-promotion agencies, industrial parks, and economic-development teams. It turns an investor pipeline into a transparent, prioritized portfolio of opportunities.

## Features

- Executive dashboard for pipeline value, jobs, stages, and sectors
- Investor CRM with filtering, search, notes, contacts, and ownership
- Transparent weighted scoring with seven investment criteria
- Automatic priority classification
- Side-by-side opportunity comparison with radar charts
- Follow-up tracker with overdue indicators
- CSV exports and management summaries
- Persistent SQLite database and realistic demo dataset
- Automated tests, Docker, and GitHub Actions

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

Open http://localhost:8501. Demo data is inserted automatically the first time the app runs.

## Run tests

```bash
python -m pytest -q
```

## Docker

```bash
docker compose up --build
```

## Scoring model

| Criterion | Weight |
|---|---:|
| Investment amount | 25% |
| Potential jobs | 20% |
| Export potential | 15% |
| Environmental performance | 15% |
| Financial strength | 10% |
| Technology transfer | 10% |
| Implementation readiness | 5% |

The model is deliberately transparent. Organizations should calibrate the weights and normalization thresholds to match their approved investment strategy.

## GitHub description

> Python investment-attraction intelligence platform with investor scoring, pipeline analytics, opportunity comparison, follow-up tracking, SQLite, Streamlit, tests, Docker, and CI.

## Suggested roadmap

- Authentication and role-based access
- PostgreSQL deployment and migrations
- Email and calendar reminders
- Document management and investor data rooms
- Configurable scoring models by sector
- AI-assisted investor brief generation
