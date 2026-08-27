from pydantic import BaseModel
from typing import Optional, List, Any

class TimelineEvent(BaseModel):
    timestamp: str
    event_type: str
    ip_address: str
    device_id: str
    geo_country: str
    amount: Optional[float] = None

class EvidenceItem(BaseModel):
    evidence_id: str
    signal: str
    weight: int
    value: Any

class Case(BaseModel):
    case_id: str
    account_id: str
    created_at: str
    rule_risk_score: float
    ml_risk_score: float
    timeline: List[TimelineEvent]
    evidence: List[EvidenceItem]
    status: str
    ai_summary: Optional[str] = None
    reviewed_at: Optional[str] = None
    reviewer_action: Optional[str] = None

class ReviewAction(BaseModel):
    action: str