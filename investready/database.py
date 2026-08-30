import csv
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from investready.scoring import calculate_score


STAGES = ["Prospect", "Qualified", "Engaged", "Due Diligence", "Negotiation", "Committed"]
STATUSES = ["Active", "On Hold", "Won", "Lost"]
SECTORS = ["Agro-processing", "Textile & Apparel", "Pharmaceuticals", "ICT", "Automotive", "Renewable Energy", "Logistics", "Manufacturing", "Other"]


def db_path() -> Path:
    return Path(os.getenv("INVESTREADY_DB", "data/investready.db"))


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize() -> None:
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS investors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL UNIQUE,
                country TEXT NOT NULL,
                sector TEXT NOT NULL,
                contact_name TEXT NOT NULL DEFAULT '',
                contact_email TEXT NOT NULL DEFAULT '',
                investment_usd_m REAL NOT NULL CHECK(investment_usd_m >= 0),
                jobs INTEGER NOT NULL CHECK(jobs >= 0),
                export_percent REAL NOT NULL CHECK(export_percent BETWEEN 0 AND 100),
                environmental_score REAL NOT NULL CHECK(environmental_score BETWEEN 0 AND 10),
                financial_score REAL NOT NULL CHECK(financial_score BETWEEN 0 AND 10),
                technology_score REAL NOT NULL CHECK(technology_score BETWEEN 0 AND 10),
                readiness_score REAL NOT NULL CHECK(readiness_score BETWEEN 0 AND 10),
                total_score REAL NOT NULL,
                category TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                owner TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS followups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
                due_date TEXT NOT NULL,
                action TEXT NOT NULL,
                owner TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_investor_stage ON investors(stage);
            CREATE INDEX IF NOT EXISTS idx_investor_score ON investors(total_score);
            CREATE INDEX IF NOT EXISTS idx_followup_due ON followups(due_date);
            """
        )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_investor(data: dict) -> int:
    score = calculate_score(
        data["investment_usd_m"], data["jobs"], data["export_percent"],
        data["environmental_score"], data["financial_score"],
        data["technology_score"], data["readiness_score"],
    )
    now = utc_now()
    with connect() as db:
        cursor = db.execute(
            """INSERT INTO investors
            (company,country,sector,contact_name,contact_email,investment_usd_m,jobs,
             export_percent,environmental_score,financial_score,technology_score,
             readiness_score,total_score,category,stage,status,owner,notes,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["company"].strip(), data["country"].strip(), data["sector"],
             data.get("contact_name", "").strip(), data.get("contact_email", "").strip(),
             data["investment_usd_m"], data["jobs"], data["export_percent"],
             data["environmental_score"], data["financial_score"], data["technology_score"],
             data["readiness_score"], score.total, score.category, data["stage"],
             data.get("status", "Active"), data.get("owner", "").strip(),
             data.get("notes", "").strip(), now, now),
        )
        return int(cursor.lastrowid)


def get_investors() -> list[dict]:
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM investors ORDER BY total_score DESC")]


def update_stage(investor_id: int, stage: str) -> None:
    if stage not in STAGES:
        raise ValueError("Invalid pipeline stage")
    with connect() as db:
        db.execute("UPDATE investors SET stage=?, updated_at=? WHERE id=?", (stage, utc_now(), investor_id))


def delete_investor(investor_id: int) -> None:
    with connect() as db:
        db.execute("DELETE FROM investors WHERE id=?", (investor_id,))


def add_followup(investor_id: int, due_date: str, action: str, owner: str) -> int:
    with connect() as db:
        cursor = db.execute(
            "INSERT INTO followups(investor_id,due_date,action,owner,created_at) VALUES (?,?,?,?,?)",
            (investor_id, due_date, action.strip(), owner.strip(), utc_now()),
        )
        return int(cursor.lastrowid)


def get_followups() -> list[dict]:
    with connect() as db:
        query = """SELECT f.*, i.company FROM followups f
                   JOIN investors i ON i.id=f.investor_id
                   ORDER BY f.completed, f.due_date"""
        return [dict(row) for row in db.execute(query)]


def toggle_followup(followup_id: int, completed: bool) -> None:
    with connect() as db:
        db.execute("UPDATE followups SET completed=? WHERE id=?", (int(completed), followup_id))


def export_csv() -> str:
    import io
    rows = get_investors()
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def seed_demo_data() -> None:
    if get_investors():
        return
    samples = [
        {"company":"Solara Manufacturing","country":"Germany","sector":"Renewable Energy","contact_name":"Anna Weber","contact_email":"anna@example.com","investment_usd_m":95.0,"jobs":720,"export_percent":85,"environmental_score":9,"financial_score":9,"technology_score":9,"readiness_score":8,"stage":"Due Diligence","owner":"Investment Team","notes":"Solar component assembly opportunity."},
        {"company":"Nile Pharma Group","country":"Egypt","sector":"Pharmaceuticals","contact_name":"Omar Hassan","contact_email":"omar@example.com","investment_usd_m":62.0,"jobs":950,"export_percent":55,"environmental_score":8,"financial_score":8,"technology_score":7,"readiness_score":9,"stage":"Negotiation","owner":"Life Sciences Desk","notes":"Regional pharmaceutical manufacturing hub."},
        {"company":"Kibo Agro Foods","country":"Kenya","sector":"Agro-processing","contact_name":"Wanjiku Njoroge","contact_email":"wanjiku@example.com","investment_usd_m":28.0,"jobs":580,"export_percent":65,"environmental_score":8,"financial_score":7,"technology_score":6,"readiness_score":7,"stage":"Engaged","owner":"Agro Desk","notes":"Fruit processing and cold-chain facility."},
        {"company":"BlueRoute Logistics","country":"UAE","sector":"Logistics","contact_name":"Layla Noor","contact_email":"layla@example.com","investment_usd_m":45.0,"jobs":240,"export_percent":75,"environmental_score":6,"financial_score":9,"technology_score":8,"readiness_score":6,"stage":"Qualified","owner":"Logistics Desk","notes":"Integrated logistics and bonded warehouse."},
        {"company":"Atlas Textiles","country":"Türkiye","sector":"Textile & Apparel","contact_name":"Emre Kaya","contact_email":"emre@example.com","investment_usd_m":34.0,"jobs":1350,"export_percent":90,"environmental_score":5,"financial_score":7,"technology_score":6,"readiness_score":5,"stage":"Prospect","owner":"Manufacturing Desk","notes":"Environmental improvement plan required."},
        {"company":"Nova Mobility","country":"China","sector":"Automotive","contact_name":"Li Wei","contact_email":"li@example.com","investment_usd_m":120.0,"jobs":1100,"export_percent":70,"environmental_score":8,"financial_score":9,"technology_score":10,"readiness_score":7,"stage":"Committed","owner":"Strategic Projects","notes":"Electric vehicle component production."},
    ]
    ids = [add_investor(item) for item in samples]
    add_followup(ids[0], (date.today() + timedelta(days=2)).isoformat(), "Send site utility specifications", "Investment Team")
    add_followup(ids[1], (date.today() - timedelta(days=1)).isoformat(), "Confirm incentive package meeting", "Life Sciences Desk")
    add_followup(ids[2], (date.today() + timedelta(days=7)).isoformat(), "Arrange industrial park visit", "Agro Desk")
