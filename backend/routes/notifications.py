from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import NotificationItem, NotificationReadResponse
from services.notifications import (
    get_notifications,
    mark_notification_read,
    mark_all_notifications_read
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationItem])
def list_notifications(
    is_read: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves list of system notifications with optional read status filter."""
    return get_notifications(is_read=is_read, db=db)


@router.post("/{notification_id}/read", response_model=NotificationReadResponse)
def read_single_notification(notification_id: str, db: Session = Depends(get_db)):
    """Marks a single notification as read."""
    success = mark_notification_read(notification_id=notification_id, db=db)
    if not success:
        raise HTTPException(status_code=404, detail=f"Notification '{notification_id}' not found.")
    return {"success": True, "marked_count": 1}


@router.post("/read-all", response_model=NotificationReadResponse)
def read_all_notifications(db: Session = Depends(get_db)):
    """Marks all unread notifications as read."""
    count = mark_all_notifications_read(db=db)
    return {"success": True, "marked_count": count}
