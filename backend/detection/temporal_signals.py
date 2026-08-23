import pandas as pd

def extract(account_events: pd.DataFrame) -> dict:
    events = account_events.sort_values("timestamp").reset_index(drop=True)
    failed_logins = events[events["event_type"] == "login_failed"]
    failed_count = len(failed_logins)

    burst_rate = 0.0
    if failed_count >= 2:
        ts = failed_logins["timestamp"]
        window = pd.Timedelta(minutes=5)
        max_in_window = 0
        for t in ts:
            count = ((ts >= t) & (ts < t + window)).sum()
            max_in_window = max(max_in_window, count)
        burst_rate = max_in_window / 5.0

    pw_events = events[events["event_type"] == "password_changed"]
    time_to_password_change_sec = None
    if len(pw_events) > 0:
        first_ts = events["timestamp"].iloc[0]
        time_to_password_change_sec = (pw_events["timestamp"].iloc[0] - first_ts).total_seconds()

    cred_events = events[events["event_type"].isin(["password_changed", "email_changed"])]
    txn_events = events[events["event_type"] == "transaction"]
    time_to_transaction_sec = None
    if len(cred_events) > 0 and len(txn_events) > 0:
        last_cred_ts = cred_events["timestamp"].max()
        first_txn_ts = txn_events["timestamp"].min()
        delta = (first_txn_ts - last_cred_ts).total_seconds()
        time_to_transaction_sec = delta if delta >= 0 else None

    event_span_sec = (events["timestamp"].max() - events["timestamp"].min()).total_seconds()

    return {
        "failed_login_count": failed_count,
        "failed_login_burst_rate": burst_rate,
        "time_to_password_change_sec": time_to_password_change_sec,
        "time_to_transaction_sec": time_to_transaction_sec,
        "event_span_sec": event_span_sec,
    }