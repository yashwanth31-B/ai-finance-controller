import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.notifications import create_notification

client = TestClient(app)


def test_get_notifications():
    """Verify GET /api/notifications returns list of notification objects."""
    response = client.get("/api/notifications")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) > 0
    first = items[0]
    assert "notification_id" in first
    assert "type" in first
    assert "title" in first
    assert "message" in first


def test_mark_notification_read():
    """Verify POST /api/notifications/{id}/read marks item as read."""
    # Create notification
    notif = create_notification(type="INFO", title="Test Alert", message="Unit test notification item")
    notif_id = notif["notification_id"]

    # Mark as read
    resp = client.post(f"/api/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    # Confirm read in GET
    list_resp = client.get("/api/notifications")
    items = list_resp.json()
    matched = [n for n in items if n["notification_id"] == notif_id]
    assert len(matched) == 1
    assert matched[0]["is_read"] is True


def test_mark_all_notifications_read():
    """Verify POST /api/notifications/read-all marks all unread notifications."""
    resp = client.post("/api/notifications/read-all")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
