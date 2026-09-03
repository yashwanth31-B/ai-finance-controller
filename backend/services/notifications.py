"""
Notification Service
====================
Manages creation, query, and read state persistence for real reconciliation system alerts.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from database import SessionLocal
from models import NotificationDB


def create_notification(
    type: str,
    title: str,
    message: str,
    invoice_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    role: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """Creates and persists a new system notification log entry."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        notif_id = f"notif-{uuid.uuid4().hex[:8]}"
        now_dt = datetime.utcnow()
        item = NotificationDB(
            notification_id=notif_id,
            role=role,
            type=type.upper(),
            title=title,
            message=message,
            invoice_id=invoice_id,
            batch_id=batch_id,
            is_read=False,
            created_at=now_dt
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        return {
            "notification_id": item.notification_id,
            "type": item.type,
            "title": item.title,
            "message": item.message,
            "invoice_id": item.invoice_id,
            "batch_id": item.batch_id,
            "is_read": item.is_read,
            "created_at": item.created_at.isoformat() if item.created_at else now_dt.isoformat()
        }
    finally:
        if close_db:
            db.close()


def get_notifications(
    is_read: Optional[bool] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Retrieves all notifications ordered by most recent, with optional read state filter."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        query = db.query(NotificationDB)
        if is_read is not None:
            query = query.filter(NotificationDB.is_read == is_read)

        items = query.order_by(NotificationDB.id.desc()).all()

        # Seed initial system event notifications if database is empty
        if not items and is_read is None:
            create_notification(
                type="WARNING",
                title="System Initialized",
                message="Multi-source 3-way reconciliation engine ready for batch execution.",
                db=db
            )
            items = db.query(NotificationDB).order_by(NotificationDB.id.desc()).all()

        return [
            {
                "notification_id": item.notification_id,
                "type": item.type,
                "title": item.title,
                "message": item.message,
                "invoice_id": item.invoice_id,
                "batch_id": item.batch_id,
                "is_read": item.is_read,
                "created_at": item.created_at.isoformat() if item.created_at else ""
            }
            for item in items
        ]
    finally:
        if close_db:
            db.close()


def mark_notification_read(notification_id: str, db: Optional[Session] = None) -> bool:
    """Marks a single notification as read."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        item = db.query(NotificationDB).filter(NotificationDB.notification_id == notification_id.strip()).first()
        if item:
            item.is_read = True
            db.commit()
            return True
        return False
    finally:
        if close_db:
            db.close()


def mark_all_notifications_read(db: Optional[Session] = None) -> int:
    """Marks all notifications as read."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        count = db.query(NotificationDB).filter(NotificationDB.is_read == False).update({"is_read": True})
        db.commit()
        return count
    finally:
        if close_db:
            db.close()
