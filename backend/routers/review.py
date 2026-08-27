from fastapi import APIRouter, HTTPException
from datetime import datetime
import db
from models import ReviewAction

router = APIRouter(prefix="/cases", tags=["review"])

VALID_ACTIONS = {"approve", "hold", "escalate"}

@router.post("/{case_id}/review")
def review_case(case_id: str, action: ReviewAction):
    if action.action not in VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"action must be one of {VALID_ACTIONS}")
    case = db.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    new_status = "closed" if action.action in ("approve", "hold") else "escalated"
    db.update_case_review(case_id, new_status, datetime.now().isoformat(), action.action)
    return db.get_case(case_id)