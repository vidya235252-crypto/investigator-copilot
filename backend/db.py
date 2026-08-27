import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "investigator.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            rule_risk_score REAL NOT NULL,
            ml_risk_score REAL NOT NULL,
            timeline TEXT NOT NULL,
            evidence TEXT NOT NULL,
            status TEXT NOT NULL,
            ai_summary TEXT,
            reviewed_at TEXT,
            reviewer_action TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_case(case: dict):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO cases (case_id, account_id, created_at, rule_risk_score, ml_risk_score, timeline, evidence, status, ai_summary, reviewed_at, reviewer_action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case["case_id"],
            case["account_id"],
            case["created_at"],
            case["rule_risk_score"],
            case["ml_risk_score"],
            json.dumps(case["timeline"]),
            json.dumps(case["evidence"]),
            case["status"],
            case.get("ai_summary"),
            case.get("reviewed_at"),
            case.get("reviewer_action"),
        ),
    )
    conn.commit()
    conn.close()

def get_case(case_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return _row_to_case(row)

def list_cases(status: str = None):
    conn = get_connection()
    if status:
        rows = conn.execute("SELECT * FROM cases WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_case(row) for row in rows]

def update_case_review(case_id: str, status: str, reviewed_at: str, reviewer_action: str):
    conn = get_connection()
    conn.execute(
        "UPDATE cases SET status = ?, reviewed_at = ?, reviewer_action = ? WHERE case_id = ?",
        (status, reviewed_at, reviewer_action, case_id),
    )
    conn.commit()
    conn.close()

def update_case_ai_summary(case_id: str, ai_summary: str):
    conn = get_connection()
    conn.execute("UPDATE cases SET ai_summary = ? WHERE case_id = ?", (ai_summary, case_id))
    conn.commit()
    conn.close()

def _row_to_case(row):
    return {
        "case_id": row["case_id"],
        "account_id": row["account_id"],
        "created_at": row["created_at"],
        "rule_risk_score": row["rule_risk_score"],
        "ml_risk_score": row["ml_risk_score"],
        "timeline": json.loads(row["timeline"]),
        "evidence": json.loads(row["evidence"]),
        "status": row["status"],
        "ai_summary": row["ai_summary"],
        "reviewed_at": row["reviewed_at"],
        "reviewer_action": row["reviewer_action"],
    }