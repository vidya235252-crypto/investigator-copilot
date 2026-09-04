# InvestigatorCopilot

**An AI investigation copilot that detects and investigates account-takeover-driven payment abuse before it becomes financial loss.**

Built for the Razorpay AI Buildathon 2026 — AI Risk Manager track.

---

## What this is

Most fraud tools answer **"is this transaction risky?"** InvestigatorCopilot answers a different question: **"how was this account compromised, and what's the evidence?"**

It applies SOC-style incident investigation methodology — evidence collection, timeline reconstruction, human-in-the-loop review — to account-takeover-driven payment abuse, a loss class that sits upstream of most transaction-level fraud scoring.

The AI never decides whether an account is compromised. A deterministic/ML risk engine does that, using explicit behavioral, temporal, and transaction signals. The AI's job is strictly to **synthesize and explain evidence that already exists** — reconstructing the incident timeline, prioritizing signals, and recommending next steps for a human reviewer. It cannot see raw event data and cannot invent evidence outside what the detection engine already surfaced.

## Why this problem

Account takeover is the precursor to a large share of payment abuse, but most fraud tooling scores the **transaction**, not the **account compromise sequence** that led to it. By the time a transaction-level model flags a payment, the account may already be fully compromised.

This project detects and investigates the compromise itself — credential changes, device/IP shifts, payment instrument changes — as an evolving incident, not an isolated event.

## Architecture

```text
Synthetic Event Stream

        ↓

Detection Engine (behavioral / temporal / transaction signals)

        ↓

Risk Engine (weighted rules + sklearn classifier)

        ↓

Evidence Collector (structured JSON, tied to raw signals)

        ↓

Investigation Case Builder

        ↓

AI Investigator (evidence-grounded synthesis only — never invents facts)

        ↓

FastAPI backend → Dashboard (timeline, evidence panel, risk score)

        ↓

Human Review (approve / hold / escalate)
```

Full architecture detail: [`docs/architecture.md`](docs/architecture.md)

## Results (held-out test set, n=120)

|               | Precision | Recall |    F1 | False Positive Rate |
| ------------- | --------: | -----: | ----: | ------------------: |
| ML classifier |     1.000 |  0.925 | 0.961 |               0.000 |
| Rule engine   |     0.667 |  1.000 | 0.800 |               0.250 |

**Structured evidence reduces estimated investigator reading time by 45.8% versus raw event logs.**

Full methodology, including a traced false positive and stated limitations, is documented in [`docs/evaluation_methodology.md`](docs/evaluation_methodology.md).

## Detection scope (MVP)

Focused narrowly on one loss class: **credential-abuse-driven account takeover**, following the sequence:

```text
New login context → New device/IP → Credential changes →
Payment instrument change → Behavioral anomaly →
Unusual/high-value transaction → ATO suspected
```

Seven labeled synthetic scenarios (legitimate account change, benign new device, legitimate password reset, credential compromise, credential stuffing, full account takeover, full ATO with payment abuse) — see [`data/scenarios.py`](data/scenarios.py).

## Evaluation

Evaluated on a held-out test set never used for threshold tuning:

* **Detection quality:** precision, recall, F1, PR-AUC, confusion matrix, false-positive rate with cost interpretation
* **Operational value:** manual vs. copilot-assisted triage time comparison

Full methodology and known limitations: [`docs/evaluation_methodology.md`](docs/evaluation_methodology.md)

Results: [`evaluation_report/`](evaluation_report/)

## Tech stack

* **Backend:** Python, FastAPI
* **ML/data:** pandas, NumPy, scikit-learn
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript, Chart.js
* **AI:** LLM via provider abstraction, with a deterministic fallback when no API key is available (demo never breaks)

## Project status

Complete — built for the Razorpay AI Buildathon 2026, AI Risk Manager track.

## Setup

```bash
git clone https://github.com/vidya235252-crypto/investigator-copilot.git
cd investigator-copilot
python -m venv venv
venv\Scripts\activate          
pip install -r requirements.txt
python data/generate_dataset.py
```

If using an LLM provider, copy `.env.example` to `.env` and add the required API key. The system falls back to deterministic evidence-grounded output when no API key is available.

### Run the backend

```bash
cd backend
python seed_cases.py
uvicorn main:app --reload
```

API available at `http://127.0.0.1:8000`, interactive docs at `/docs`.

### Run the dashboard

Open `frontend/index.html` directly in a browser. The backend must be running.

### Reproduce evaluation

```bash
cd backend
python run_evaluation.py
```

Outputs held-out test metrics to `evaluation_report/metrics.json`, plus confusion matrix and triage-time charts as PNGs.

## Project structure

```text
investigator-copilot/
├── data/               # synthetic dataset generator and scenario definitions
├── backend/            # FastAPI app: detection, evidence, AI investigator, routers
├── frontend/           # dashboard: timeline, evidence panel, risk gauge
├── notebooks/          # threshold tuning scratch space (train/val only)
├── evaluation_report/  # held-out test metrics, confusion matrix, triage-time results
└── docs/               # architecture, evaluation methodology, demo script
```

## License

TBD.
