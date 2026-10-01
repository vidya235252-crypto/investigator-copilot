"""
Backfill ml_explanation for cases that were built before ml_explainer.py existed.

Run from the backend/ folder:
    python backfill_ml_explanations.py

It re-extracts each case's account signals from data/raw/events.csv, runs the
explainer, and UPDATEs only the ml_explanation column for that case_id.
Status, notes, ai_summary, reviewed_at and reviewer_action are untouched.

If a case's account_id isn't found in events.csv (e.g. you point this at a
different dataset than the case was built from), that case is skipped and
reported at the end, nothing is written for it.
"""
import json
import sqlite3
import sys

import pandas as pd

from detection import ml_risk_model, ml_explainer, behavioral_signals, temporal_signals, transaction_signals

DB_PATH = "investigator.db"
EVENTS_PATH = "../data/raw/events.csv"
MODEL_PATH = "detection/risk_model.joblib"


def extract_signals(events_for_account):
    return {
        **behavioral_signals.extract(events_for_account),
        **temporal_signals.extract(events_for_account),
        **transaction_signals.extract(events_for_account),
    }


def main():
    events = pd.read_csv(EVENTS_PATH, parse_dates=["timestamp"])
    model = ml_risk_model.load_model(MODEL_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT case_id, account_id FROM cases WHERE ml_explanation IS NULL"
    ).fetchall()

    if not rows:
        print("Nothing to backfill — every case already has an ml_explanation.")
        return

    updated, skipped = 0, []
    for row in rows:
        acct_events = events[events.account_id == row["account_id"]]
        if acct_events.empty:
            skipped.append(row["account_id"])
            continue

        signals = extract_signals(acct_events)
        explanation = ml_explainer.explain(model, signals)
        drivers = [
            {
                "evidence_id": f"mlev_{row['case_id'][5:13]}_{i}",
                "signal": d["signal"],
                "weight": d["weight"],
                "value": d["value"],
            }
            for i, d in enumerate(explanation["drivers"])
        ]
        payload = {
            "base_score": explanation["base_score"],
            "drivers": drivers,
            "other": explanation["other"],
        }
        conn.execute(
            "UPDATE cases SET ml_explanation = ? WHERE case_id = ?",
            (json.dumps(payload), row["case_id"]),
        )
        updated += 1

    conn.commit()
    conn.close()

    print(f"Backfilled {updated} case(s).")
    if skipped:
        print(f"Skipped {len(skipped)} case(s) with no matching account in {EVENTS_PATH}:")
        for a in skipped:
            print(f"  - {a}")


if __name__ == "__main__":
    main()
