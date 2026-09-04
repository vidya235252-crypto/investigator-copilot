# InvestigatorCopilot

**An AI investigation copilot that detects and investigates account-takeover-driven payment abuse before it becomes financial loss.**

Built for the **Razorpay AI Buildathon 2026 — AI Risk Manager track.**

---

## What this is

Most fraud tools answer **"is this transaction risky?"** InvestigatorCopilot answers a different question:

> **"How was this account compromised, and what's the evidence?"**

It applies SOC-style incident investigation methodology — evidence collection, timeline reconstruction, and human-in-the-loop review — to account-takeover-driven payment abuse, a loss class that sits upstream of most transaction-level fraud scoring.

The AI never decides whether an account is compromised. A deterministic/ML risk engine does that using explicit behavioral, temporal, and transaction signals.

The AI's job is strictly to **synthesize and explain evidence that already exists** — reconstructing the incident timeline, prioritizing signals, and recommending next steps for a human reviewer.

It cannot see raw event data and cannot invent evidence outside what the detection engine already surfaced.

---

## Why this problem

Account takeover is the precursor to a large share of payment abuse, but most fraud tooling scores the **transaction**, not the **account compromise sequence** that led to it.

By the time a transaction-level model flags a payment, the account may already be fully compromised.

InvestigatorCopilot instead treats account takeover as an **evolving incident**:

```text
Credential / login anomaly
        ↓
Device / IP change
        ↓
Credential changes
        ↓
Payment instrument change
        ↓
Behavioral anomaly
        ↓
Unusual / high-value transaction
        ↓
Account takeover suspected
```

The goal is not simply to flag suspicious activity, but to give an investigator a structured explanation of **what happened, why it matters, and what evidence supports the conclusion.**

---

## Architecture

```text
Synthetic Event Stream

        ↓

Detection Engine
(behavioral / temporal / transaction signals)

        ↓

Risk Engine
(weighted rules + sklearn classifier)

        ↓

Evidence Collector
(structured JSON, tied to raw signals)

        ↓

Investigation Case Builder

        ↓

AI Investigator
(evidence-grounded synthesis only — never invents facts)

        ↓

FastAPI backend → Dashboard
(timeline, evidence panel, risk score, entity graph,
 analyst notes, case actions)

        ↓

Human Review
(approve / hold / escalate)
```

Full architecture detail: [`docs/architecture.md`](docs/architecture.md)

### Core design principle

**AI explains. Detection systems detect. Humans decide.**

The AI investigator operates only on structured evidence produced by the detection and case-building layers. This keeps the generative component useful without giving it independent authority over risk decisions.

---

## Results

### Held-out test set — n=120

|                   | Precision | Recall |    F1 | False Positive Rate |
| ----------------- | --------: | -----: | ----: | ------------------: |
| **ML classifier** |     1.000 |  0.925 | 0.961 |               0.000 |
| **Rule engine**   |     0.667 |  1.000 | 0.800 |               0.250 |

**Structured evidence reduces estimated investigator reading time by 45.8% versus raw event logs.**

The evaluation includes held-out testing, threshold selection using training/validation data, false-positive tracing, and cost interpretation.

Full methodology, including the traced false positive and stated limitations, is documented in [`docs/evaluation_methodology.md`](docs/evaluation_methodology.md).

---

## Detection scope (MVP)

The MVP focuses narrowly on one loss class:

**Credential-abuse-driven account takeover and subsequent payment abuse.**

The detection pipeline combines behavioral, temporal, and transaction signals such as:

* New login context
* New device
* IP changes
* Credential changes
* Payment instrument changes
* Behavioral anomalies
* Transaction amount / velocity signals
* Temporal relationships between suspicious events

The resulting signals are passed into a weighted rule engine and sklearn classifier before structured evidence is generated for investigation.

---

## Synthetic scenarios

Seven labeled synthetic scenarios are used to evaluate the system across both malicious and legitimate behavior:

1. **Legitimate account change**
2. **Benign new device**
3. **Legitimate password reset**
4. **Credential compromise**
5. **Credential stuffing**
6. **Full account takeover**
7. **Full ATO with payment abuse**

Scenario definitions and event generation are available in [`data/scenarios.py`](data/scenarios.py).

The legitimate scenarios are intentionally included to test false-positive behavior rather than evaluating only obvious attack cases.

---

## Investigation workflow

When suspicious activity is detected, InvestigatorCopilot builds a structured investigation case rather than sending raw events directly to an LLM.

### 1. Detection

Behavioral, temporal, and transaction signals are extracted from the event stream.

### 2. Risk assessment

A combination of weighted rules and an sklearn classifier evaluates the account's risk.

### 3. Evidence collection

Relevant signals are converted into structured evidence tied back to the underlying events.

### 4. Case construction

The system organizes the evidence into an investigation case with a chronological incident timeline.

### 5. AI investigation

The AI investigator synthesizes the existing evidence into:

* Incident summary
* Attack progression
* Key risk signals
* Timeline interpretation
* Evidence-backed reasoning
* Recommended next investigative actions

The AI is explicitly constrained from inventing facts that are not present in the supplied evidence.

### 6. Human review

The final decision remains with the analyst, who can take case actions such as:

* **Approve**
* **Hold**
* **Escalate**

Analyst notes are also supported for retaining investigation context during a session. Notes are currently stored locally in the browser rather than persisted to the case record on the server — see [Limitations](#limitations).

---

## Evidence-grounded AI

A central design requirement is that the LLM should **not become the fraud detector**.

Instead:

```text
Raw events
    ↓
Detection engine
    ↓
Risk signals
    ↓
Structured evidence
    ↓
Investigation case
    ↓
AI synthesis
```

The AI receives the evidence selected by the investigation pipeline rather than unrestricted access to the raw event stream.

This creates a clear separation of responsibilities:

| Component          | Responsibility               |
| ------------------ | ----------------------------- |
| Detection engine   | Extract suspicious signals   |
| Risk engine        | Assess risk                  |
| Evidence collector | Preserve supporting evidence |
| Case builder       | Organize the incident        |
| AI investigator    | Explain and synthesize       |
| Human analyst      | Make the final decision      |

---

## Evaluation

The system is evaluated on a held-out test set that is not used for threshold tuning.

### Detection quality

Evaluation includes:

* Precision
* Recall
* F1 score
* PR-AUC
* Confusion matrix
* False-positive rate
* Cost interpretation

### Operational value

The project also measures the estimated time required for an investigator to understand an incident using:

1. Raw event logs
2. Structured evidence generated by InvestigatorCopilot

This provides an operational measure in addition to model-level classification metrics.

Full methodology and known limitations: [`docs/evaluation_methodology.md`](docs/evaluation_methodology.md)

Evaluation outputs: [`evaluation_report/`](evaluation_report/)

---

## Dashboard

The dashboard provides an analyst-facing investigation workspace containing:

* Account information
* Device and IP context
* Risk score
* Incident timeline
* Evidence panel
* Entity relationship graph
* Analyst notes
* Case actions
* Investigation summary

The interface is designed around the investigation workflow rather than presenting the system as a generic chatbot.

---

## Reliability and fallback behavior

The AI layer uses a provider abstraction so the investigation workflow does not depend entirely on an external LLM API.

When an LLM API key is unavailable or an API call fails, the system falls back to deterministic evidence-grounded output.

This means the core demo and investigation workflow can continue without an external model dependency.

The fallback path was explicitly verified during development.

See [`docs/architecture.md`](docs/architecture.md) for implementation details.

---

## Tech stack

* **Backend:** Python, FastAPI
* **ML/data:** pandas, NumPy, scikit-learn
* **Database:** SQLite
* **Frontend:** HTML, CSS, JavaScript
* **AI:** LLM via provider abstraction with deterministic fallback

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/vidya235252-crypto/investigator-copilot.git
cd investigator-copilot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Generate the dataset

```bash
python data/generate_dataset.py
```

If using an LLM provider, copy `.env.example` to `.env` and add the required API key.

The system falls back to deterministic evidence-grounded output when no API key is available or the call fails.

---

## Run the backend

From the project root:

```bash
cd backend
python seed_cases.py
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Run the dashboard

With the backend running, open:

```text
frontend/index.html
```

directly in a browser.

The dashboard communicates with the locally running FastAPI backend.

---

## Reproduce evaluation

From the project root:

```bash
cd backend
python run_evaluation.py
```

The evaluation produces:

* Held-out test metrics
* `metrics.json`
* Confusion matrix
* Triage-time comparison charts

Outputs are written to:

```text
evaluation_report/
```

---

## Project structure

```text
investigator-copilot/
├── data/               # synthetic dataset generator and scenario definitions
├── backend/            # FastAPI app: detection, evidence, AI investigator, routers
├── frontend/           # dashboard: timeline, evidence panel, entity graph, notes
├── evaluation_report/  # held-out test metrics, confusion matrix, triage-time results
└── docs/               # architecture, evaluation methodology, demo script
```

---

## Project status

**Complete — built for the Razorpay AI Buildathon 2026, AI Risk Manager track.**

---

## Limitations

This is an MVP research/buildathon implementation and is intentionally scoped.

* The dataset is synthetic rather than production payment data.
* The current detection scope focuses on credential-abuse-driven account takeover.
* Real-world fraud behavior is substantially more diverse than the seven modeled scenarios.
* Evaluation results should not be interpreted as production performance.
* The AI investigator is an analyst-assistance layer, not an autonomous fraud decision-maker.
* Analyst notes are stored locally in the browser (not synced server-side); a persisted version would require a small schema and endpoint addition.
* Production deployment would require additional controls around model monitoring, drift detection, data privacy, authentication, authorization, audit logging, and integration with real payment-risk infrastructure.

---

## Documentation

* [`docs/architecture.md`](docs/architecture.md) — system architecture and component responsibilities
* [`docs/evaluation_methodology.md`](docs/evaluation_methodology.md) — evaluation design, metrics, false-positive analysis, and limitations

---

## License

MIT
