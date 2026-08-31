# Architecture

## Pipeline

Synthetic Event Stream → Detection Engine (behavioral / temporal / transaction signals)
→ Risk Engine (weighted rules + trained ML classifier, run independently)
→ Evidence Collector → Investigation Case → AI Investigator (evidence-grounded synthesis,
LLM with deterministic fallback) → FastAPI backend → Dashboard → Human Review

## Design principle

The AI Investigator never determines risk. A separate deterministic rule engine and a
trained scikit-learn classifier compute risk scores from structured signals extracted
from raw account events. Only after that scoring is complete does the AI receive a
fixed evidence JSON — built once, before the AI is called, and never modified by it —
and generate a plain-language narrative and a recommended action. It has no access to
raw events, cannot query the database, and cannot introduce facts outside the evidence
object it was given. A human analyst makes the final decision through the dashboard's
review workflow, which is persisted and auditable.

## Why both a rule engine and an ML model

The rule engine is fully transparent: every point in its score traces to a specific,
named signal with a fixed weight. This makes it defensible and easy to explain, but
its performance ceiling is lower — hand-weighted thresholds cannot capture interactions
between signals the way a trained model can. The ML classifier (Random Forest) learns
these interactions from labeled training data and achieves substantially higher
precision, at the cost of being less directly interpretable per prediction. Keeping
both gives an investigator a transparent baseline alongside a higher-confidence signal,
and surfaces disagreements between them as a signal worth investigating on its own.

## Components

- `data/` — synthetic account-activity generator, 7 labeled scenarios, seeded and
  reproducible, stratified 60/20/20 train/val/test split by account.
- `backend/detection/` — signal extraction (behavioral, temporal, transaction),
  rule-based risk engine, trained ML risk classifier.
- `backend/evidence/` — builds the timeline and evidence list from raw events and
  signals; the single boundary between detection and everything downstream.
- `backend/ai/` — evidence-grounded LLM investigator with a deterministic fallback
  template used when no API key is present or the call fails, verified to keep the
  system fully functional with zero external dependency.
- `backend/routers/` — FastAPI endpoints: case listing, case detail, AI investigation
  trigger, human review actions.
- `backend/evaluation/` — held-out test metrics (precision/recall/F1/PR-AUC/confusion
  matrix, both engines) and a triage-time estimate.
- `frontend/` — investigation queue and case detail dashboard (vanilla HTML/CSS/JS),
  including timeline reconstruction, evidence panel, derived account/device/IP summary,
  a lightweight entity-relationship graph, and browser-local analyst notes.

## Known limitations

- Analyst notes are stored in browser `localStorage`, not synced to the case record in
  the backend. This was a deliberate scope decision to avoid backend schema changes
  mid-build; a persisted version requires one additional table and two endpoints.
- The `is_new_ip_country` signal was removed during development (see commit history)
  because the dataset lacks a pre-incident baseline period per account, making the
  signal structurally unable to fire. A real deployment would need historical account
  data outside the incident window to support this signal.
- Triage-time reduction is a word-count reading-time proxy, not a timed user study —
  stated explicitly in `evaluation_methodology.md`.