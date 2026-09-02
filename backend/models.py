import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class ReconciliationBatch(Base):
    """Placeholder model for tracking multi-source batch reconciliation runs."""
    __tablename__ = "reconciliation_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String, index=True)
    total_records = Column(Integer, default=0)
    matched_records = Column(Integer, default=0)
    exceptions_count = Column(Integer, default=0)
    match_rate = Column(Float, default=0.0)
    accuracy_rate = Column(Float, default=0.0)
    throughput_records_per_sec = Column(Float, default=0.0)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
