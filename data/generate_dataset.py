import os
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from scenarios import SCENARIOS

load_dotenv()
SEED = int(os.getenv("RANDOM_SEED", 42))
random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SCENARIO_COUNTS = {
    "legitimate_account_change": 220,
    "new_device_legitimate": 180,
    "credential_compromise": 70,
    "credential_stuffing": 60,
    "full_account_takeover": 45,
    "ato_with_payment_abuse": 25,
}

WINDOW_DAYS = 60

def _random_start_time():
    offset_days = random.uniform(0, WINDOW_DAYS)
    offset_seconds = random.uniform(0, 86400)
    return datetime(2026, 6, 1) + timedelta(days=offset_days, seconds=offset_seconds)

def generate_all():
    all_events = []
    all_labels = []

    for scenario_name, count in SCENARIO_COUNTS.items():
        fn = SCENARIOS[scenario_name]
        for _ in range(count):
            start_time = _random_start_time()
            account_id, events, label = fn(start_time)
            all_events.extend(events)
            all_labels.append({
                "account_id": account_id,
                "scenario_type": scenario_name,
                "is_ato": label,
            })

    events_df = pd.DataFrame(all_events)
    labels_df = pd.DataFrame(all_labels)
    return events_df, labels_df

def stratified_split(labels_df, train_frac=0.6, val_frac=0.2):
    splits = []
    for scenario_type, group in labels_df.groupby("scenario_type"):
        shuffled = group.sample(frac=1, random_state=SEED).reset_index(drop=True)
        n = len(shuffled)
        n_train = int(n * train_frac)
        n_val = int(n * val_frac)
        shuffled.loc[:n_train - 1, "split"] = "train"
        shuffled.loc[n_train:n_train + n_val - 1, "split"] = "val"
        shuffled.loc[n_train + n_val:, "split"] = "test"
        splits.append(shuffled)
    return pd.concat(splits, ignore_index=True)

def main():
    events_df, labels_df = generate_all()
    labels_df = stratified_split(labels_df)

    events_path = os.path.join(OUTPUT_DIR, "events.csv")
    labels_path = os.path.join(OUTPUT_DIR, "labels.csv")
    events_df.to_csv(events_path, index=False)
    labels_df.to_csv(labels_path, index=False)

    print("scenario counts:")
    print(labels_df["scenario_type"].value_counts())
    print()
    print("split counts:")
    print(labels_df["split"].value_counts())
    print()
    print("split x scenario:")
    print(pd.crosstab(labels_df["split"], labels_df["scenario_type"]))
    print()
    print("class balance (is_ato) by split:")
    print(pd.crosstab(labels_df["split"], labels_df["is_ato"], normalize="index"))
    print()
    print(f"total events: {len(events_df)}")
    print(f"total accounts: {len(labels_df)}")
    print(f"written to: {events_path}, {labels_path}")

if __name__ == "__main__":
    main()