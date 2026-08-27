def generate_fallback_summary(case):
    top_signals = sorted(case["evidence"], key=lambda e: e["weight"], reverse=True)[:3]
    signal_text = ", ".join(s["signal"].replace("_", " ") for s in top_signals)
    event_count = len(case["timeline"])
    first_event = case["timeline"][0]["event_type"] if case["timeline"] else "unknown"
    last_event = case["timeline"][-1]["event_type"] if case["timeline"] else "unknown"

    score = case["ml_risk_score"]
    if score >= 80:
        action = "escalate"
    elif score >= 40:
        action = "hold"
    else:
        action = "approve"

    summary = (
        f"This account shows {event_count} recorded events, beginning with {first_event.replace('_', ' ')} "
        f"and ending with {last_event.replace('_', ' ')}. The strongest contributing signals are: {signal_text}. "
        f"Combined risk scores (rule-based: {case['rule_risk_score']}, ML: {case['ml_risk_score']}) indicate "
        f"a pattern consistent with account takeover risk. This summary was generated using a deterministic "
        f"fallback template, not an LLM call.\n\nRECOMMENDED_ACTION: {action}"
    )
    return summary