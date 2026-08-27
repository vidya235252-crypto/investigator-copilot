from fastapi import APIRouter, HTTPException
import db
from ai import investigator


router = APIRouter(prefix="/cases", tags=["cases"])

@router.get("")
def get_cases(status: str = None):
    return db.list_cases(status)

@router.get("/{case_id}")
def get_case_detail(case_id: str):
    case = db.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    return case

@router.post("/{case_id}/investigate")
def investigate_case(case_id: str):
    case = db.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    summary = investigator.generate_summary(case)
    db.update_case_ai_summary(case_id, summary)
    return db.get_case(case_id)