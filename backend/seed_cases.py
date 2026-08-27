import pandas as pd
from detection import ml_risk_model
from evidence import case_builder
import db

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")

db.init_db()

model = ml_risk_model.load_model("detection/risk_model.joblib")

flagged_scenarios = ["ato_with_payment_abuse", "full_account_takeover", "credential_compromise", "credential_stuffing"]

count = 0
for scenario in flagged_scenarios:
    sample_accounts = labels[labels["scenario_type"] == scenario].head(5)
    for _, row in sample_accounts.iterrows():
        account_events = events[events["account_id"] == row["account_id"]]
        case = case_builder.build_case(row["account_id"], account_events, model)
        db.insert_case(case)
        count += 1

print(f"seeded {count} cases")