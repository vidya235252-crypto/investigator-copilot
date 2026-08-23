import uuid
import random
from datetime import datetime, timedelta

def _new_account_id():
    return f"acct_{uuid.uuid4().hex[:8]}"

def _jittered_gap(mean_seconds, std_seconds=10):
    return max(1, random.gauss(mean_seconds, std_seconds))

def _base_event(account_id, event_type, ts, ip, device, geo, amount=None, metadata=None):
    return {
        "event_id": f"evt_{uuid.uuid4().hex[:8]}",
        "account_id": account_id,
        "event_type": event_type,
        "timestamp": ts,
        "ip_address": ip,
        "device_id": device,
        "geo_country": geo,
        "amount": amount,
        "metadata": metadata or {},
    }

def legitimate_account_change(start_time, inject_payment_change_rate=0.15):
    ...

def new_device_legitimate(start_time):
    ...

def credential_compromise(start_time):
    ...

def credential_stuffing(start_time):
    ...

def full_account_takeover(start_time):
    ...

def ato_with_payment_abuse(start_time):
    ...

SCENARIOS = {
    "legitimate_account_change": (legitimate_account_change, 0),
    "new_device_legitimate": (new_device_legitimate, 0),
    "credential_compromise": (credential_compromise, 1),
    "credential_stuffing": (credential_stuffing, 1),
    "full_account_takeover": (full_account_takeover, 1),
    "ato_with_payment_abuse": (ato_with_payment_abuse, 1),
}