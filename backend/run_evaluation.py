import json
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from detection import ml_risk_model, risk_engine, behavioral_signals, temporal_signals, transaction_signals
from evidence import case_builder
from ai import investigator
from evaluation import metrics, triage_time

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "evaluation_report")
os.makedirs(OUTPUT_DIR, exist_ok=True)

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")
test_labels = labels[labels["split"] == "test"].reset_index(drop=True)
val_labels = labels[labels["split"] == "val"].reset_index(drop=True)

model = ml_risk_model.load_model("detection/risk_model.joblib")

X_test, y_test = ml_risk_model.build_dataset(events, labels, "test")
ml_proba = model.predict_proba(X_test)[:, 1]
ml_pred = (ml_proba >= ml_risk_model.DEFAULT_THRESHOLD).astype(int)

def score_accounts(label_rows):
    scores = []
    scenario_list = []
    y = []
    for _, row in label_rows.iterrows():
        account_events = events[events["account_id"] == row["account_id"]]
        signals = {
            **behavioral_signals.extract(account_events),
            **temporal_signals.extract(account_events),
            **transaction_signals.extract(account_events),
        }
        result = risk_engine.rule_based_score(signals)
        scores.append(result["risk_score"])
        scenario_list.append(row["scenario_type"])
        y.append(row["is_ato"])
    return pd.Series(scores), pd.Series(y), scenario_list

def tune_rule_threshold(val_scores, val_y):
    best_threshold, best_f1 = 25, 0
    for t in [8, 10, 12, 15, 20, 25, 30, 40, 50]:
        pred = (val_scores >= t).astype(int)
        f1 = metrics.binary_metrics(val_y, pred)["f1"]
        if f1 > best_f1:
            best_f1, best_threshold = f1, t
    return best_threshold, best_f1

val_scores, val_y, _ = score_accounts(val_labels)
RULE_THRESHOLD, tuned_val_f1 = tune_rule_threshold(val_scores, val_y)
print(f"tuned rule threshold on val: {RULE_THRESHOLD} (val F1: {tuned_val_f1})")

rule_scores, _, scenario_list = score_accounts(test_labels)
rule_pred = (rule_scores >= RULE_THRESHOLD).astype(int)

ml_metrics = metrics.binary_metrics(y_test, ml_pred)
ml_metrics["pr_auc"] = metrics.pr_auc(y_test, ml_proba)
ml_metrics["per_scenario_recall"] = metrics.per_scenario_recall(y_test, ml_pred, scenario_list)

rule_metrics = metrics.binary_metrics(y_test, rule_pred)
rule_metrics["pr_auc"] = metrics.pr_auc(y_test, rule_scores / 100.0)
rule_metrics["per_scenario_recall"] = metrics.per_scenario_recall(y_test, rule_pred, scenario_list)

sample_accounts = test_labels[test_labels["is_ato"] == 1].head(10)
triage_cases = []
for _, row in sample_accounts.iterrows():
    account_events = events[events["account_id"] == row["account_id"]]
    case = case_builder.build_case(row["account_id"], account_events, model)
    case["ai_summary"] = investigator.generate_summary(case)
    triage_cases.append(case)

triage_result = triage_time.compute_triage_comparison(triage_cases)

report = {
    "test_set_size": len(test_labels),
    "ml_model": ml_metrics,
    "rule_engine": rule_metrics,
    "triage_time": triage_result,
    "thresholds_used": {
        "ml_threshold": ml_risk_model.DEFAULT_THRESHOLD,
        "rule_threshold": RULE_THRESHOLD,
        "rule_threshold_tuning_val_f1": tuned_val_f1,
    },
}

with open(os.path.join(OUTPUT_DIR, "metrics.json"), "w") as f:
    json.dump(report, f, indent=2)

cm = ml_metrics["confusion_matrix"]
fig, ax = plt.subplots(figsize=(4, 4))
matrix = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
ax.imshow(matrix, cmap="Blues")
for i in range(2):
    for j in range(2):
        ax.text(j, i, matrix[i][j], ha="center", va="center", fontsize=14)
ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(["Predicted Legit", "Predicted ATO"])
ax.set_yticklabels(["Actual Legit", "Actual ATO"])
ax.set_title("ML Model — Held-Out Test Confusion Matrix")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "confusion_matrix.png"))
plt.close()

fig, ax = plt.subplots(figsize=(5, 4))
labels_bar = ["Manual\n(raw timeline)", "Copilot\n(structured evidence)"]
values = [triage_result["avg_manual_seconds"], triage_result["avg_structured_evidence_seconds"]]
ax.bar(labels_bar, values, color=["#8a8f98", "#5b87b0"])
ax.set_ylabel("Estimated seconds per case")
ax.set_title(f"Triage Time (est.) — {triage_result['structured_evidence_reduction_percent']}% reduction")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "triage_time_comparison.png"))
plt.close()

print(json.dumps(report, indent=2))
print(f"\nsaved to {OUTPUT_DIR}")