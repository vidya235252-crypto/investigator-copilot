WORDS_PER_MINUTE = 200

def estimate_manual_reading_seconds(timeline):
    words = 0
    for e in timeline:
        words += len(f"{e['timestamp']} {e['event_type']} {e['ip_address']} {e['device_id']} {e['geo_country']} {e.get('amount', '')}".split())
    return (words / WORDS_PER_MINUTE) * 60

def estimate_evidence_only_seconds(evidence):
    words = sum(len(f"{ev['signal']} {ev['weight']} {ev['value']}".split()) for ev in evidence)
    return (words / WORDS_PER_MINUTE) * 60

def compute_triage_comparison(cases):
    manual_times = []
    evidence_times = []
    summary_times = []
    for c in cases:
        manual_times.append(estimate_manual_reading_seconds(c["timeline"]))
        evidence_times.append(estimate_evidence_only_seconds(c["evidence"]))
        summary_words = len(c["ai_summary"].split()) if c.get("ai_summary") else 0
        summary_times.append((summary_words / WORDS_PER_MINUTE) * 60)

    avg_manual = sum(manual_times) / len(manual_times) if manual_times else 0
    avg_evidence = sum(evidence_times) / len(evidence_times) if evidence_times else 0
    avg_summary = sum(summary_times) / len(summary_times) if summary_times else 0
    reduction_pct = ((avg_manual - avg_evidence) / avg_manual * 100) if avg_manual > 0 else 0

    return {
        "avg_manual_seconds": round(avg_manual, 1),
        "avg_structured_evidence_seconds": round(avg_evidence, 1),
        "avg_ai_summary_seconds_optional": round(avg_summary, 1),
        "structured_evidence_reduction_percent": round(reduction_pct, 1),
        "n_cases": len(cases),
        "methodology": f"Primary comparison is reading the full raw event timeline (manual) vs. the structured evidence list alone (copilot), both as word-count proxies at {WORDS_PER_MINUTE} words/minute. The AI narrative summary is reported separately as optional supplementary reading, since a real investigator would consult it for ambiguous cases rather than always reading it in full. This is a reading-time proxy, not a timed user study.",
    }