import uuid
from datetime import datetime
from detection import behavioral_signals, temporal_signals, transaction_signals, risk_engine, ml_risk_model
from evidence import collector

def build_case(account_id, account_events, model):
    signals = {
        **behavioral_signals.extract(account_events),
        **temporal_signals.extract(account_events),
        **transaction_signals.extract(account_events),
    }
    rule_result = risk_engine.rule_based_score(signals)
    ml_score = ml_risk_model.predict_risk_score(model, signals)

    timeline = collector.build_timeline(account_events)
    evidence = collector.build_evidence_list(signals, rule_result["contributing_signals"])

    return {
        "case_id": f"case_{uuid.uuid4().hex[:8]}",
        "account_id": account_id,
        "created_at": datetime.now().isoformat(),
        "rule_risk_score": rule_result["risk_score"],
        "ml_risk_score": ml_score,
        "timeline": timeline,
        "evidence": evidence,
        "status": "open",
    }