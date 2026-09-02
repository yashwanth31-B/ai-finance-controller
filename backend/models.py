import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from database import Base


class ReconciliationBatch(Base):
    """Tracking model for multi-source batch reconciliation runs."""
    __tablename__ = "reconciliation_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True, unique=True)
    batch_name = Column(String, index=True)
    total_records = Column(Integer, default=0)
    matched_records = Column(Integer, default=0)
    exceptions_count = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    accuracy_rate = Column(Float, default=0.0)
    throughput_records_per_sec = Column(Float, default=0.0)
    status = Column(String, default="COMPLETED")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ReviewActionDB(Base):
    """Immutable record of human review decisions."""
    __tablename__ = "review_actions"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String, index=True, unique=True)
    batch_id = Column(String, index=True, nullable=True)
    invoice_id = Column(String, index=True)
    reconciliation_result_id = Column(String, nullable=True)
    original_system_status = Column(String)
    original_confidence_score = Column(Float)
    original_bank_transaction_id = Column(String, nullable=True)
    original_gateway_payment_id = Column(String, nullable=True)
    review_action = Column(String)  # APPROVE_MATCH, REJECT_MATCH, MARK_RESOLVED, KEEP_UNDER_REVIEW
    reviewer_name = Column(String, default="Finance Reviewer")
    reviewer_note = Column(Text, nullable=True)
    previous_final_status = Column(String)
    new_final_status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditEventDB(Base):
    """Immutable audit trail log entry for all financial controller compliance events."""
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, index=True, unique=True)
    event_type = Column(String, index=True)  # REVIEW_APPROVED, REVIEW_REJECTED, etc.
    invoice_id = Column(String, index=True)
    batch_id = Column(String, index=True, nullable=True)
    actor = Column(String)
    previous_state = Column(String)
    new_state = Column(String)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
