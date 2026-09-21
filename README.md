<div align="center">

# 📊 InvestReady

**Investment-attraction intelligence for stronger, more transparent pipelines.**

![Python](https://img.shields.io/badge/Python-071A2D?style=for-the-badge&logo=python&logoColor=F7DF1E)
![Streamlit](https://img.shields.io/badge/Streamlit-071A2D?style=for-the-badge&logo=streamlit&logoColor=FF4B4B)
![SQLite](https://img.shields.io/badge/SQLite-071A2D?style=for-the-badge&logo=sqlite&logoColor=22D3EE)
![Docker](https://img.shields.io/badge/Docker-071A2D?style=for-the-badge&logo=docker&logoColor=2496ED)

</div>

## Overview

InvestReady is a decision-support platform for investment-promotion agencies, industrial parks, and economic-development teams. It converts an investor pipeline into an explainable, prioritized portfolio.

<!-- Upload a real screenshot as docs/investready-dashboard.png, then uncomment:
![InvestReady executive dashboard](docs/investready-dashboard.png)
-->

## Features

- Executive pipeline dashboard
- Searchable investor CRM and stage management
- Seven-criterion weighted opportunity scoring
- Automatic priority classification
- Side-by-side comparison with radar charts
- Follow-up tracker with overdue alerts
- CSV exports and management summaries
- Persistent SQLite database and demo dataset
- Automated tests, Docker, and CI support

## Technology

`Python` · `Streamlit` · `Pandas` · `Plotly` · `SQLite` · `Pytest` · `Docker`

## Run locally

```bash
git clone https://github.com/ahvi27/INVESTREADY-PLATFORM.git
cd INVESTREADY-PLATFORM
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

Open `http://localhost:8501`. Demo data is created automatically.

### Docker

```bash
docker compose up --build
```

### Tests

```bash
python -m pytest -q
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

## Author

Built by [Gelila Mulugeta](https://github.com/ahvi27).
