import uuid

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

def build_evidence_list(signals, contributing_signals):
    evidence = []
    for item in contributing_signals:
        evidence.append({
            "evidence_id": f"ev_{uuid.uuid4().hex[:8]}",
            "signal": item["signal"],
            "weight": item["weight"],
            "value": item["value"],
        })
    return evidence