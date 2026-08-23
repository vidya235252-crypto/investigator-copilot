RULE_WEIGHTS = {
    "is_new_device": 8,
    "password_changed": 15,
    "email_changed": 15,
    "payment_instrument_added": 12,
    "credential_change_count_2plus": 10,
    "failed_login_burst_rate_high": 12,
    "fast_time_to_password_change": 10,
    "fast_time_to_transaction": 15,
    "payment_instrument_change_before_transaction": 20,
    "high_transaction_velocity": 8,
}

def rule_based_score(signals: dict) -> dict:
    contributing = []
    total = 0

    if signals.get("is_new_device"):
        total += RULE_WEIGHTS["is_new_device"]
        contributing.append({"signal": "is_new_device", "weight": RULE_WEIGHTS["is_new_device"], "value": True})

    if signals.get("password_changed"):
        total += RULE_WEIGHTS["password_changed"]
        contributing.append({"signal": "password_changed", "weight": RULE_WEIGHTS["password_changed"], "value": True})

    if signals.get("email_changed"):
        total += RULE_WEIGHTS["email_changed"]
        contributing.append({"signal": "email_changed", "weight": RULE_WEIGHTS["email_changed"], "value": True})

    if signals.get("payment_instrument_added"):
        total += RULE_WEIGHTS["payment_instrument_added"]
        contributing.append({"signal": "payment_instrument_added", "weight": RULE_WEIGHTS["payment_instrument_added"], "value": True})

    if signals.get("credential_change_count", 0) >= 2:
        total += RULE_WEIGHTS["credential_change_count_2plus"]
        contributing.append({"signal": "credential_change_count_2plus", "weight": RULE_WEIGHTS["credential_change_count_2plus"], "value": signals["credential_change_count"]})

    if signals.get("failed_login_burst_rate", 0) >= 1.0:
        total += RULE_WEIGHTS["failed_login_burst_rate_high"]
        contributing.append({"signal": "failed_login_burst_rate_high", "weight": RULE_WEIGHTS["failed_login_burst_rate_high"], "value": signals["failed_login_burst_rate"]})

    ttpc = signals.get("time_to_password_change_sec")
    if ttpc is not None and ttpc < 300:
        total += RULE_WEIGHTS["fast_time_to_password_change"]
        contributing.append({"signal": "fast_time_to_password_change", "weight": RULE_WEIGHTS["fast_time_to_password_change"], "value": ttpc})

    ttt = signals.get("time_to_transaction_sec")
    if ttt is not None and ttt < 900:
        total += RULE_WEIGHTS["fast_time_to_transaction"]
        contributing.append({"signal": "fast_time_to_transaction", "weight": RULE_WEIGHTS["fast_time_to_transaction"], "value": ttt})

    if signals.get("payment_instrument_change_before_transaction"):
        total += RULE_WEIGHTS["payment_instrument_change_before_transaction"]
        contributing.append({"signal": "payment_instrument_change_before_transaction", "weight": RULE_WEIGHTS["payment_instrument_change_before_transaction"], "value": True})

    if signals.get("transaction_velocity", 0) >= 1.0:
        total += RULE_WEIGHTS["high_transaction_velocity"]
        contributing.append({"signal": "high_transaction_velocity", "weight": RULE_WEIGHTS["high_transaction_velocity"], "value": signals["transaction_velocity"]})

    risk_score = min(100, total)
    contributing.sort(key=lambda c: c["weight"], reverse=True)

    return {"risk_score": risk_score, "contributing_signals": contributing}