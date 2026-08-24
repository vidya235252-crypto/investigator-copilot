import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from detection import behavioral_signals, temporal_signals, transaction_signals

FEATURE_ORDER = [
    "is_new_device",
    "password_changed",
    "email_changed",
    "payment_instrument_added",
    "credential_change_count",
    "failed_login_count",
    "failed_login_burst_rate",
    "time_to_password_change_sec",
    "time_to_transaction_sec",
    "event_span_sec",
    "transaction_count",
    "total_transaction_amount",
    "max_transaction_amount",
    "transaction_velocity",
    "payment_instrument_change_before_transaction",
]

SENTINEL = 999999.0

def build_feature_vector(signals: dict) -> list:
    vector = []
    for key in FEATURE_ORDER:
        value = signals.get(key)
        if value is None:
            value = SENTINEL
        elif isinstance(value, bool) or isinstance(value, np.bool_):
            value = int(value)
        vector.append(float(value))
    return vector

def build_dataset(events_df, labels_df, split_name):
    split_labels = labels_df[labels_df["split"] == split_name]
    X, y = [], []
    for _, row in split_labels.iterrows():
        account_events = events_df[events_df["account_id"] == row["account_id"]]
        signals = {
            **behavioral_signals.extract(account_events),
            **temporal_signals.extract(account_events),
            **transaction_signals.extract(account_events),
        }
        X.append(build_feature_vector(signals))
        y.append(row["is_ato"])
    return np.array(X), np.array(y)

def train(events_df, labels_df):
    X_train, y_train = build_dataset(events_df, labels_df, "train")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=5,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)
    return model

def save_model(model, path="risk_model.joblib"):
    joblib.dump(model, path)

def load_model(path="risk_model.joblib"):
    return joblib.load(path)

def predict_risk_score(model, signals: dict) -> float:
    vector = np.array([build_feature_vector(signals)])
    proba = model.predict_proba(vector)[0][1]
    return round(proba * 100, 2)