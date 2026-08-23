import uuid
import random
from datetime import datetime, timedelta

import uuid
import random
from datetime import datetime, timedelta

def _new_account_id():
    return f"acct_{uuid.uuid4().hex[:8]}"

def _new_device_id():
    return f"dev_{uuid.uuid4().hex[:8]}"

def _random_ip():
    return f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

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
    account_id = _new_account_id()
    home_ip = _random_ip()
    home_device = _new_device_id()
    geo = random.choice(["IN", "IN", "IN", "US"])
    events = []
    ts = start_time

    events.append(_base_event(account_id, "login", ts, home_ip, home_device, geo))

    ts += timedelta(seconds=_jittered_gap(3600 * 24, 3600))
    new_device = _new_device_id()
    events.append(_base_event(account_id, "device_registered", ts, home_ip, new_device, geo))

    ts += timedelta(seconds=_jittered_gap(60, 20))
    events.append(_base_event(account_id, "login", ts, home_ip, new_device, geo))

    if random.random() < inject_payment_change_rate:
        ts += timedelta(seconds=_jittered_gap(300, 60))
        events.append(_base_event(account_id, "payment_instrument_added", ts, home_ip, new_device, geo))

    ts += timedelta(seconds=_jittered_gap(3600, 900))
    events.append(_base_event(account_id, "transaction", ts, home_ip, new_device, geo, amount=round(random.uniform(200, 3000), 2)))

    return account_id, events, 0

def new_device_legitimate(start_time):
    account_id = _new_account_id()
    geo = random.choice(["IN", "IN", "US"])
    new_ip = _random_ip()
    new_device = _new_device_id()
    events = []
    ts = start_time

    events.append(_base_event(account_id, "login", ts, new_ip, new_device, geo))

    ts += timedelta(seconds=_jittered_gap(1800, 300))
    events.append(_base_event(account_id, "device_registered", ts, new_ip, new_device, geo))

    ts += timedelta(seconds=_jittered_gap(3600 * 6, 1800))
    events.append(_base_event(account_id, "transaction", ts, new_ip, new_device, geo, amount=round(random.uniform(100, 1500), 2)))

    return account_id, events, 0

def credential_compromise(start_time):
    account_id = _new_account_id()
    geo_home = "IN"
    geo_new = random.choice(["US", "SG", "AE"])
    attacker_ip = _random_ip()
    attacker_device = _new_device_id()
    events = []
    ts = start_time

    for _ in range(random.randint(2, 4)):
        ts += timedelta(seconds=_jittered_gap(15, 5))
        events.append(_base_event(account_id, "login_failed", ts, attacker_ip, attacker_device, geo_new, metadata={"reason": "bad_password"}))

    ts += timedelta(seconds=_jittered_gap(10, 3))
    events.append(_base_event(account_id, "login", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(90, 30))
    events.append(_base_event(account_id, "password_changed", ts, attacker_ip, attacker_device, geo_new))

    return account_id, events, 1

def credential_stuffing(start_time):
    account_id = _new_account_id()
    geo_new = random.choice(["RU", "NG", "BR", "US"])
    attacker_ip = _random_ip()
    attacker_device = _new_device_id()
    events = []
    ts = start_time

    for _ in range(random.randint(5, 9)):
        ts += timedelta(seconds=_jittered_gap(4, 2))
        events.append(_base_event(account_id, "login_failed", ts, attacker_ip, attacker_device, geo_new, metadata={"reason": "bad_password"}))

    ts += timedelta(seconds=_jittered_gap(5, 2))
    events.append(_base_event(account_id, "login", ts, attacker_ip, attacker_device, geo_new))

    return account_id, events, 1

def full_account_takeover(start_time):
    account_id = _new_account_id()
    geo_new = random.choice(["US", "NG", "RU"])
    attacker_ip = _random_ip()
    attacker_device = _new_device_id()
    events = []
    ts = start_time

    events.append(_base_event(account_id, "login", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(60, 15))
    events.append(_base_event(account_id, "device_registered", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(120, 30))
    events.append(_base_event(account_id, "password_changed", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(180, 40))
    events.append(_base_event(account_id, "email_changed", ts, attacker_ip, attacker_device, geo_new))

    return account_id, events, 1

def ato_with_payment_abuse(start_time):
    account_id = _new_account_id()
    geo_new = random.choice(["US", "NG", "RU", "AE"])
    attacker_ip = _random_ip()
    attacker_device = _new_device_id()
    events = []
    ts = start_time

    events.append(_base_event(account_id, "login", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(90, 20))
    events.append(_base_event(account_id, "device_registered", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(150, 30))
    events.append(_base_event(account_id, "password_changed", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(120, 25))
    events.append(_base_event(account_id, "email_changed", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(180, 40))
    events.append(_base_event(account_id, "payment_instrument_added", ts, attacker_ip, attacker_device, geo_new))

    ts += timedelta(seconds=_jittered_gap(240, 50))
    events.append(_base_event(account_id, "transaction", ts, attacker_ip, attacker_device, geo_new, amount=round(random.uniform(35000, 52000), 2)))

    ts += timedelta(seconds=_jittered_gap(90, 20))
    events.append(_base_event(account_id, "transaction", ts, attacker_ip, attacker_device, geo_new, amount=round(random.uniform(60000, 85000), 2)))

    return account_id, events, 1

SCENARIOS = {
    "legitimate_account_change": legitimate_account_change,
    "new_device_legitimate": new_device_legitimate,
    "credential_compromise": credential_compromise,
    "credential_stuffing": credential_stuffing,
    "full_account_takeover": full_account_takeover,
    "ato_with_payment_abuse": ato_with_payment_abuse,
}
