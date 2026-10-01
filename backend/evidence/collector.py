import uuid
import numpy as np

def build_timeline(account_events):
    events = account_events.sort_values("timestamp")
    timeline = []
    for _, row in events.iterrows():
        timeline.append({
            "timestamp": row["timestamp"].isoformat(),
            "event_type": row["event_type"],
            "ip_address": row["ip_address"],
            "device_id": row["device_id"],
            "geo_country": row["geo_country"],
            "amount": row["amount"] if row["amount"] == row["amount"] else None,
        })
    return timeline

def _to_native(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value

def build_evidence_list(signals, contributing_signals):
    evidence = []
    for item in contributing_signals:
        evidence.append({
            "evidence_id": f"ev_{uuid.uuid4().hex[:8]}",
            "signal": item["signal"],
            "weight": item["weight"],
            "value": _to_native(item["value"]),
        })
    return evidence

def build_ml_explanation(explanation):
    """Attach evidence ids to the ML explainer output so drivers can be cited like rule evidence."""
    drivers = []
    for item in explanation["drivers"]:
        drivers.append({
            "evidence_id": f"mlev_{uuid.uuid4().hex[:8]}",
            "signal": item["signal"],
            "weight": item["weight"],          # signed points the feature moved the ML score
            "value": _to_native(item["value"]),  # None = event never occurred for this account
        })
    return {
        "base_score": explanation["base_score"],
        "drivers": drivers,
        "other": explanation["other"],
    }
