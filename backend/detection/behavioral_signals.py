import pandas as pd

def extract(account_events: pd.DataFrame) -> dict:
    events = account_events.sort_values("timestamp")
    device_events = events[events["event_type"] == "device_registered"]
    return {
        "is_new_device": len(device_events) > 0,
        "password_changed": (events["event_type"] == "password_changed").any(),
        "email_changed": (events["event_type"] == "email_changed").any(),
        "payment_instrument_added": (events["event_type"] == "payment_instrument_added").any(),
        "credential_change_count": (events["event_type"].isin(["password_changed", "email_changed"])).sum(),
    }