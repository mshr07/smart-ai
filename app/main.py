"""SmartDesk AI: one API connecting AI inference to an SQLite database."""

import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "ticket_model.joblib"
logger = logging.getLogger("smartdesk")
logging.basicConfig(level=logging.INFO)


class TicketInput(BaseModel):
    text: str = Field(min_length=10, max_length=2000)


def db_path():
    return Path(os.environ.get("DB_PATH", str(ROOT / "runtime" / "tickets.db")))


def connect_db():
    return sqlite3.connect(db_path(), timeout=10)


def initialize_database():
    db_path().parent.mkdir(parents=True, exist_ok=True)
    with connect_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                confidence REAL NOT NULL,
                needs_review INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )


@lru_cache(maxsize=1)
def get_model():
    # Never load untrusted model files; joblib uses Python pickle internally.
    return joblib.load(MODEL_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    get_model()
    yield


app = FastAPI(title="SmartDesk AI", version="1.0", lifespan=lifespan)


def priority_for(text):
    urgent_phrases = ("urgent", "asap", "immediately", "charged twice", "fraud")
    return "high" if any(word in text.lower() for word in urgent_phrases) else "normal"


@app.get("/health")
def health():
    get_model()
    with connect_db() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "ok", "model_ready": True, "database_ready": True}


@app.post("/tickets", status_code=201)
def create_ticket(payload: TicketInput):
    model = get_model()
    category = str(model.predict([payload.text])[0])
    confidence = float(max(model.predict_proba([payload.text])[0]))
    priority = priority_for(payload.text)
    needs_review = confidence < 0.60
    with connect_db() as conn:
        cursor = conn.execute(
            """INSERT INTO tickets
            (text, category, priority, confidence, needs_review)
            VALUES (?, ?, ?, ?, ?)""",
            (payload.text, category, priority, confidence, int(needs_review)),
        )
        ticket_id = cursor.lastrowid
    logger.info("Ticket %s created, category=%s", ticket_id, category)
    return {
        "ticket_id": ticket_id,
        "category": category,
        "priority": priority,
        "confidence": round(confidence, 3),
        "needs_review": needs_review,
        "status": "created",
    }


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    with connect_db() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    result = dict(row)
    result["needs_review"] = bool(result["needs_review"])
    return result


@app.get("/metrics")
def metrics():
    with connect_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        categories = dict(
            conn.execute(
                "SELECT category, COUNT(*) FROM tickets GROUP BY category"
            ).fetchall()
        )
        review = conn.execute(
            "SELECT COUNT(*) FROM tickets WHERE needs_review = 1"
        ).fetchone()[0]
    return {"tickets_total": total, "by_category": categories, "needs_review": review}
