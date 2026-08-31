import pandas as pd
from detection import ml_risk_model, risk_engine, behavioral_signals, temporal_signals, transaction_signals

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")
test_labels = labels[(labels["split"] == "test") & (labels["is_ato"] == 0)]

model = ml_risk_model.load_model("detection/risk_model.joblib")
RULE_THRESHOLD = 10

candidates = []
for _, row in test_labels.iterrows():
    account_events = events[events["account_id"] == row["account_id"]]
    signals = {
        **behavioral_signals.extract(account_events),
        **temporal_signals.extract(account_events),
        **transaction_signals.extract(account_events),
    }
    rule_result = risk_engine.rule_based_score(signals)
    ml_score = ml_risk_model.predict_risk_score(model, signals)
    if rule_result["risk_score"] >= RULE_THRESHOLD:
        candidates.append({
            "account_id": row["account_id"],
            "scenario_type": row["scenario_type"],
            "rule_score": rule_result["risk_score"],
            "ml_score": ml_score,
            "contributing": [c["signal"] for c in rule_result["contributing_signals"]],
        })

candidates.sort(key=lambda c: c["ml_score"])
for c in candidates[:5]:
    print(c)