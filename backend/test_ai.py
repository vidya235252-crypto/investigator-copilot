import pandas as pd
from detection import ml_risk_model
from evidence import case_builder
from ai import investigator

events = pd.read_csv("../data/raw/events.csv", parse_dates=["timestamp"])
labels = pd.read_csv("../data/raw/labels.csv")

model = ml_risk_model.load_model("detection/risk_model.joblib")
account_id = labels[labels["scenario_type"] == "ato_with_payment_abuse"].iloc[0]["account_id"]
account_events = events[events["account_id"] == account_id]
case = case_builder.build_case(account_id, account_events, model)

summary = investigator.generate_summary(case)
print(summary)