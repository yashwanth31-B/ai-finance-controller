"""
Human Review & Audit Trail Service
===================================
Manages manual finance reviewer decisions, derives final status without mutating original system predictions,
maintains immutable audit trail entries, and handles database persistence.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ReviewActionDB, AuditEventDB
from services.reconciliation import get_latest_results, get_result_by_invoice_id, LATEST_RECONCILIATION_BATCH
from services.exceptions import get_all_exceptions

VALID_ACTIONS = {"APPROVE_MATCH", "REJECT_MATCH", "MARK_RESOLVED", "KEEP_UNDER_REVIEW"}


def submit_review(
    invoice_id: str,
    action: str,
    reviewer_name: str = "Finance Reviewer",
    note: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Submits a human review action for an invoice record.
    Validates rules, derives final decision, updates active state, and persists immutable ReviewAction & AuditEvent records.
    """
    # 1. Input Sanitization & Validation
    invoice_id = (invoice_id or "").strip()
    action = (action or "").strip().upper()
    reviewer_name = (reviewer_name or "Finance Reviewer").strip()
    if not reviewer_name:
        reviewer_name = "Finance Reviewer"
    note = (note or "").strip()

    if len(note) > 2000:
        raise ValueError("Review note exceeds maximum allowed limit of 2000 characters.")

    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid review action '{action}'. Must be one of {sorted(list(VALID_ACTIONS))}.")

    # 2. Retrieve Invoice Reconciliation Record
    record = get_result_by_invoice_id(invoice_id)
    if not record:
        raise ValueError(f"Invoice '{invoice_id}' not found in active reconciliation batch.")

    orig_system_status = record.get("status", "UNKNOWN")
    orig_confidence = record.get("overall_confidence_score", 0.0)
    orig_bank_id = record.get("selected_bank_transaction_id")
    orig_gw_id = record.get("selected_gateway_payment_id")
    batch_id = (
        record.get("batch_id")
        or (LATEST_RECONCILIATION_BATCH.get("batch_id") if LATEST_RECONCILIATION_BATCH else None)
        or "batch_demo"
    )


    previous_final = record.get("final_status") or f"{orig_system_status}_AUTO"

    # 3. Derive Human Review Status & Final Decision
    if action == "APPROVE_MATCH":
        human_review_status = "APPROVED"
        new_final_status = "MATCHED_APPROVED"
        event_type = "REVIEW_APPROVED"
    elif action == "REJECT_MATCH":
        human_review_status = "REJECTED"
        new_final_status = "REJECTED"
        event_type = "REVIEW_REJECTED"
    elif action == "MARK_RESOLVED":
        human_review_status = "RESOLVED"
        new_final_status = "RESOLVED_MANUALLY"
        event_type = "REVIEW_MARKED_RESOLVED"
    elif action == "KEEP_UNDER_REVIEW":
        human_review_status = "UNDER_REVIEW"
        new_final_status = "UNDER_REVIEW"
        event_type = "REVIEW_RETURNED_TO_REVIEW"

    # 4. Update In-Memory Record State (Preserving original system status & scores)
    record["human_review_status"] = human_review_status
    record["final_status"] = new_final_status
    record["latest_review_action"] = action

    # 5. Exception Status Sync
    if action == "MARK_RESOLVED":
        active_exceptions = get_all_exceptions()
        for exc in active_exceptions:
            if exc.get("invoice_id") == invoice_id:
                exc["status"] = "RESOLVED"

    # 6. Database Operations
    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        now_dt = datetime.utcnow()
        now_iso = now_dt.isoformat()

        review_uuid = uuid.uuid4().hex[:8]
        review_id = f"REV-{review_uuid}"

        review_db = ReviewActionDB(
            review_id=review_id,
            batch_id=batch_id,
            invoice_id=invoice_id,
            reconciliation_result_id=record.get("reconciliation_result_id"),
            original_system_status=orig_system_status,
            original_confidence_score=orig_confidence,
            original_bank_transaction_id=orig_bank_id,
            original_gateway_payment_id=orig_gw_id,
            review_action=action,
            reviewer_name=reviewer_name,
            reviewer_note=note,
            previous_final_status=previous_final,
            new_final_status=new_final_status,
            created_at=now_dt
        )
        db.add(review_db)

        audit_uuid = uuid.uuid4().hex[:8]
        audit_id = f"AUD-{audit_uuid}"

        audit_db = AuditEventDB(
            audit_id=audit_id,
            event_type=event_type,
            invoice_id=invoice_id,
            batch_id=batch_id,
            actor=reviewer_name,
            previous_state=previous_final,
            new_state=new_final_status,
            note=note,
            created_at=now_dt
        )
        db.add(audit_db)

        db.commit()
        db.refresh(review_db)

        return {
            "review_id": review_db.review_id,
            "batch_id": review_db.batch_id,
            "invoice_id": review_db.invoice_id,
            "original_system_status": review_db.original_system_status,
            "original_confidence_score": review_db.original_confidence_score,
            "original_bank_transaction_id": review_db.original_bank_transaction_id,
            "original_gateway_payment_id": review_db.original_gateway_payment_id,
            "review_action": review_db.review_action,
            "reviewer_name": review_db.reviewer_name,
            "reviewer_note": review_db.reviewer_note,
            "previous_final_status": review_db.previous_final_status,
            "new_final_status": review_db.new_final_status,
            "created_at": now_iso
        }
    finally:
        if close_db_session:
            db.close()


def get_review_history(
    invoice_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    action: Optional[str] = None,
    reviewer_name: Optional[str] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Retrieves review history records from database with optional filters."""
    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        query = db.query(ReviewActionDB)
        if invoice_id:
            query = query.filter(ReviewActionDB.invoice_id == invoice_id.strip())
        if batch_id:
            query = query.filter(ReviewActionDB.batch_id == batch_id.strip())
        if action:
            query = query.filter(ReviewActionDB.review_action == action.strip().upper())
        if reviewer_name:
            query = query.filter(ReviewActionDB.reviewer_name == reviewer_name.strip())

        query = query.order_by(ReviewActionDB.id.desc())
        items = query.all()

        return [
            {
                "review_id": item.review_id,
                "batch_id": item.batch_id,
                "invoice_id": item.invoice_id,
                "reconciliation_result_id": item.reconciliation_result_id,
                "original_system_status": item.original_system_status,
                "original_confidence_score": item.original_confidence_score,
                "original_bank_transaction_id": item.original_bank_transaction_id,
                "original_gateway_payment_id": item.original_gateway_payment_id,
                "review_action": item.review_action,
                "reviewer_name": item.reviewer_name,
                "reviewer_note": item.reviewer_note,
                "previous_final_status": item.previous_final_status,
                "new_final_status": item.new_final_status,
                "created_at": item.created_at.isoformat() if item.created_at else ""
            }
            for item in items
        ]
    finally:
        if close_db_session:
            db.close()


def get_audit_trail_events(
    invoice_id: Optional[str] = None,
    actor: Optional[str] = None,
    event_type: Optional[str] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Retrieves audit trail event logs from database with optional filters."""
    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        query = db.query(AuditEventDB)
        if invoice_id:
            query = query.filter(AuditEventDB.invoice_id == invoice_id.strip())
        if actor:
            query = query.filter(AuditEventDB.actor == actor.strip())
        if event_type:
            query = query.filter(AuditEventDB.event_type == event_type.strip().upper())

        query = query.order_by(AuditEventDB.id.desc())
        items = query.all()

        return [
            {
                "audit_id": item.audit_id,
                "event_type": item.event_type,
                "invoice_id": item.invoice_id,
                "batch_id": item.batch_id,
                "actor": item.actor,
                "previous_state": item.previous_state,
                "new_state": item.new_state,
                "note": item.note,
                "created_at": item.created_at.isoformat() if item.created_at else ""
            }
            for item in items
        ]
    finally:
        if close_db_session:
            db.close()


def get_review_metrics(db: Optional[Session] = None) -> Dict[str, int]:
    """Computes human review operational metrics."""
    results = get_latest_results()
    reviewed_records = sum(1 for r in results if r.get("human_review_status") and r.get("human_review_status") != "NOT_REVIEWED")
    approved_matches = sum(1 for r in results if r.get("human_review_status") == "APPROVED")
    rejected_matches = sum(1 for r in results if r.get("human_review_status") == "REJECTED")
    resolved_exceptions = sum(1 for r in results if r.get("human_review_status") == "RESOLVED")
    under_review = sum(1 for r in results if r.get("human_review_status") == "UNDER_REVIEW")

    return {
        "reviewed_records": reviewed_records,
        "approved_matches": approved_matches,
        "rejected_matches": rejected_matches,
        "resolved_exceptions": resolved_exceptions,
        "under_review": under_review
    }
