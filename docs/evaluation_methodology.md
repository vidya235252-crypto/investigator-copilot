# Evaluation Methodology

## Data splitting

600 synthetic accounts across 7 labeled scenarios, split 60/20/20 into train/val/test,
stratified by scenario type and split at the account level (never mixing a single
account's events across splits). Thresholds for both the rule engine and the ML
classifier were tuned exclusively on the validation split. The test split was not
examined or used for any tuning decision until final evaluation.

## Detection quality (held-out test set, n=120)

### ML classifier (Random Forest, threshold 0.5, tuned on val)

- Precision: 1.000
- Recall: 0.925
- F1: 0.961
- False positive rate: 0.000 (0 of 80 legitimate test accounts flagged)
- PR-AUC: 0.9907

Per-scenario recall:
- ato_with_payment_abuse: 1.000 (5/5) — small sample, read directionally
- full_account_takeover: 1.000 (9/9)
- credential_stuffing: 1.000 (12/12)
- credential_compromise: 0.786 (11/14)

The only missed cases are concentrated in credential_compromise, the scenario
deliberately designed to be the subtlest — a handful of failed logins followed by a
single password change, with no device, email, or payment cascade. This is the
expected, honest failure mode of a system built for early detection: the earliest
possible signal of compromise is also the hardest to distinguish from legitimate
password-reset behavior.

### Rule engine (threshold 10, tuned on val)

- Precision: 0.667
- Recall: 1.000
- F1: 0.800
- False positive rate: 0.250 (20 of 80 legitimate test accounts flagged)
- PR-AUC: 0.7727

The rule engine catches every malicious test case but at a real precision cost. This
is the expected tradeoff of fully transparent, hand-weighted scoring versus a trained
model: full explainability, lower discriminative power. See a specific traced false
positive below.

## A traced false positive

[Fill in from find_false_positive.py output: account ID, scenario type, which rule(s)
fired, and the ML score for the same account — demonstrating the ML model correctly
did not flag it, and explain in one sentence why the rule fired.]

## Operational value: triage time

Estimated as a reading-time proxy — word count of what an investigator must read,
divided by an assumed 200 words/minute, not a timed user study.

- Manual (raw event timeline): 8.6s average per case
- Copilot (structured evidence list only): 4.7s average per case — 45.8% reduction
- AI narrative summary (optional supplementary reading): 17.1s average, reported
  separately since an investigator would consult it selectively for ambiguous cases
  rather than always reading it in full

## Limitations

- All data is synthetic; behavioral signal separation is likely cleaner than in real
  account activity, where legitimate and malicious behavior overlap more.
- ato_with_payment_abuse test recall (1.0) is based on only 5 instances.
- The AI Investigator's narrative quality could not be evaluated against real LLM
  output during most of this build due to Anthropic API billing constraints; the
  deterministic fallback path was tested explicitly and confirmed functional.

## A traced false positive

Account acct_2fc02cfb (scenario: legitimate_account_change) triggered the rule engine
at a score of 20 — above its tuned threshold of 10 — due to two signals firing:
is_new_device and payment_instrument_added. This account added a payment method
shortly after a routine device change, a pattern the rule engine cannot distinguish
from early-stage account takeover using its fixed, hand-weighted signal set.

The ML classifier scored the same account at 0.65 out of 100 — well below its 50-point
threshold — correctly recognizing the absence of the fuller compromise pattern: no
credential changes, no failed login burst, no fast time-to-transaction, no elevated
transaction velocity.

This case is the clearest evidence for keeping both engines rather than one: the rule
engine offers full transparency but lower precision, the ML classifier offers higher
precision by learning signal interactions the rule engine cannot represent, and their
disagreement on ambiguous cases like this one is itself a useful signal for a human
investigator to weigh.