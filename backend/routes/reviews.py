from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ReviewCreateRequest, ReviewActionItem, AuditEventItem
from services.review import (
    submit_review,
    get_review_history,
    get_audit_trail_events
)
from services.reconciliation import get_result_by_invoice_id

router = APIRouter(prefix="/api", tags=["reviews"])


@router.get("/reviews", response_model=List[ReviewActionItem])
def list_review_history(
    invoice_id: Optional[str] = Query(None),
    batch_id: Optional[str] = Query(None),
    review_action: Optional[str] = Query(None),
    reviewer_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves human review action history with optional filters."""
    return get_review_history(
        invoice_id=invoice_id,
        batch_id=batch_id,
        action=review_action,
        reviewer_name=reviewer_name,
        db=db
    )


@router.get("/reviews/{invoice_id}", response_model=List[ReviewActionItem])
def get_invoice_review_history(invoice_id: str, db: Session = Depends(get_db)):
    """Retrieves human review decision history for a specific invoice ID."""
    record = get_result_by_invoice_id(invoice_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found.")
    return get_review_history(invoice_id=invoice_id, db=db)


@router.post("/reviews", response_model=ReviewActionItem)
def create_review_action(payload: ReviewCreateRequest, db: Session = Depends(get_db)):
    """
    Submits a human review decision (APPROVE_MATCH, REJECT_MATCH, MARK_RESOLVED, KEEP_UNDER_REVIEW).
    Validates input rules, derives final decision, updates active state, and appends audit log.
    """
    try:
        result = submit_review(
            invoice_id=payload.invoice_id,
            action=payload.action,
            reviewer_name=payload.reviewer_name,
            note=payload.note,
            db=db
        )
        return result
    except ValueError as exc:
        msg = str(exc)
        if "not found" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.get("/audit-trail", response_model=List[AuditEventItem])
def list_audit_trail_events(
    invoice_id: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves immutable audit trail event logs with optional filters."""
    return get_audit_trail_events(
        invoice_id=invoice_id,
        actor=actor,
        event_type=event_type,
        db=db
    )
