import pandas as pd

def extract(account_events: pd.DataFrame) -> dict:
    events = account_events.sort_values("timestamp").reset_index(drop=True)
    txns = events[events["event_type"] == "transaction"]
    txn_count = len(txns)

    velocity = 0.0
    if txn_count > 1:
        span_min = (txns["timestamp"].max() - txns["timestamp"].min()).total_seconds() / 60.0
        velocity = txn_count / span_min if span_min > 0 else txn_count

    payment_added = events[events["event_type"] == "payment_instrument_added"]
    change_before_txn = False
    if len(payment_added) > 0 and txn_count > 0:
        change_before_txn = payment_added["timestamp"].min() < txns["timestamp"].min()

    return {
        "transaction_count": txn_count,
        "total_transaction_amount": txns["amount"].sum() if txn_count > 0 else 0.0,
        "max_transaction_amount": txns["amount"].max() if txn_count > 0 else 0.0,
        "transaction_velocity": velocity,
        "payment_instrument_change_before_transaction": change_before_txn,
    }