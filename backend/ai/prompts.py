SYSTEM_PROMPT = """You are a fraud investigation assistant supporting a human risk analyst.
You will be given a structured evidence JSON containing a timeline of account events and a list of weighted risk signals.
You must base your entire response only on the evidence provided. Do not invent facts, events, or signals that are not present in the input.
Your job is to explain what happened, in plain language, and recommend one action from: approve, hold, escalate.
Always end your response with a line in the exact format: RECOMMENDED_ACTION: <action>
"""

def build_user_prompt(case):
    return f"""Case ID: {case['case_id']}
Rule-based risk score: {case['rule_risk_score']}
ML risk score: {case['ml_risk_score']}

Timeline:
{_format_timeline(case['timeline'])}

Evidence signals:
{_format_evidence(case['evidence'])}

Write a concise investigation summary (4-6 sentences) explaining what happened and why this account was flagged, based strictly on the evidence above. Then recommend one action.
"""

def _format_timeline(timeline):
    lines = []
    for e in timeline:
        amount_str = f", amount={e['amount']}" if e.get("amount") else ""
        lines.append(f"- {e['timestamp']}: {e['event_type']} (ip={e['ip_address']}, device={e['device_id']}, geo={e['geo_country']}{amount_str})")
    return "\n".join(lines)

def _format_evidence(evidence):
    lines = []
    for ev in evidence:
        lines.append(f"- {ev['signal']} (weight={ev['weight']}, value={ev['value']})")
    return "\n".join(lines)