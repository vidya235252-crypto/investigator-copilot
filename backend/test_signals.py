import pandas as pd
from detection import behavioral_signals, temporal_signals, transaction_signals, risk_engine

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")

for scenario in labels["scenario_type"].unique():
    sample_account = labels[labels["scenario_type"] == scenario].iloc[0]["account_id"]
    account_events = events[events["account_id"] == sample_account]
    signals = {
        **behavioral_signals.extract(account_events),
        **temporal_signals.extract(account_events),
        **transaction_signals.extract(account_events),
    }
    result = risk_engine.rule_based_score(signals)
    print(scenario, "risk_score:", result["risk_score"])
    for c in result["contributing_signals"]:
        print(" ", c["signal"], c["weight"], c["value"])
    print()