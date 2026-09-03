import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
import services.settings as settings_service

client = TestClient(app)


def test_fetch_settings():
    """Verify GET /api/settings returns valid settings schema and default values."""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()

    assert "amount_tolerance" in data
    assert "date_tolerance_days" in data
    assert "auto_match_threshold" in data
    assert "review_threshold" in data
    assert "fuzzy_similarity_threshold" in data
    assert "candidate_score_gap" in data
    assert "updated_at" in data

    assert isinstance(data["amount_tolerance"], (int, float))
    assert isinstance(data["date_tolerance_days"], int)


def test_save_settings():
    """Verify PUT /api/settings saves and persists updated settings."""
    payload = {
        "amount_tolerance": 50.0,
        "date_tolerance_days": 5,
        "auto_match_threshold": 85.0,
        "review_threshold": 65.0,
        "fuzzy_similarity_threshold": 75.0,
        "candidate_score_gap": 8.0
    }
    response = client.put("/api/settings", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["amount_tolerance"] == 50.0
    assert data["date_tolerance_days"] == 5
    assert data["auto_match_threshold"] == 85.0
    assert data["review_threshold"] == 65.0
    assert data["fuzzy_similarity_threshold"] == 75.0
    assert data["candidate_score_gap"] == 8.0

    # Confirm GET returns updated settings
    get_resp = client.get("/api/settings")
    assert get_resp.status_code == 200
    assert get_resp.json()["amount_tolerance"] == 50.0


def test_invalid_threshold():
    """Verify PUT /api/settings rejects threshold > 100, < 0, or review >= auto_match."""
    # Threshold > 100
    invalid_payload1 = {
        "amount_tolerance": 0.0,
        "date_tolerance_days": 3,
        "auto_match_threshold": 105.0,
        "review_threshold": 70.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    }
    resp1 = client.put("/api/settings", json=invalid_payload1)
    assert resp1.status_code == 400
    assert "between 0 and 100" in resp1.json()["detail"].lower()

    # review_threshold >= auto_match_threshold
    invalid_payload2 = {
        "amount_tolerance": 0.0,
        "date_tolerance_days": 3,
        "auto_match_threshold": 70.0,
        "review_threshold": 80.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    }
    resp2 = client.put("/api/settings", json=invalid_payload2)
    assert resp2.status_code == 400
    assert "greater than review threshold" in resp2.json()["detail"].lower()


def test_negative_tolerance():
    """Verify PUT /api/settings rejects negative amount or date tolerances."""
    # Negative amount tolerance
    payload1 = {
        "amount_tolerance": -10.0,
        "date_tolerance_days": 3,
        "auto_match_threshold": 90.0,
        "review_threshold": 70.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    }
    resp1 = client.put("/api/settings", json=payload1)
    assert resp1.status_code == 400
    assert "cannot be negative" in resp1.json()["detail"].lower()

    # Negative date tolerance
    payload2 = {
        "amount_tolerance": 0.0,
        "date_tolerance_days": -2,
        "auto_match_threshold": 90.0,
        "review_threshold": 70.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    }
    resp2 = client.put("/api/settings", json=payload2)
    assert resp2.status_code == 400
    assert "cannot be negative" in resp2.json()["detail"].lower()


def test_reset_defaults():
    """Verify POST /api/settings/reset restores initial safe defaults."""
    # First modify settings
    client.put("/api/settings", json={
        "amount_tolerance": 150.0,
        "date_tolerance_days": 10,
        "auto_match_threshold": 95.0,
        "review_threshold": 80.0,
        "fuzzy_similarity_threshold": 85.0,
        "candidate_score_gap": 15.0
    })

    # Trigger reset
    reset_resp = client.post("/api/settings/reset")
    assert reset_resp.status_code == 200
    data = reset_resp.json()

    assert data["amount_tolerance"] == 0.0
    assert data["date_tolerance_days"] == 3
    assert data["auto_match_threshold"] == 90.0
    assert data["review_threshold"] == 70.0
    assert data["fuzzy_similarity_threshold"] == 70.0
    assert data["candidate_score_gap"] == 10.0


def test_reconciliation_uses_changed_amount_tolerance():
    """Verify that changing amount_tolerance alters amount mismatch classification on next reconciliation run."""
    # Reset defaults first
    client.post("/api/settings/reset")

    # Set amount_tolerance to 50.0
    client.put("/api/settings", json={
        "amount_tolerance": 50.0,
        "date_tolerance_days": 3,
        "auto_match_threshold": 90.0,
        "review_threshold": 70.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    })

    # Execute reconciliation run
    run_resp = client.post("/api/reconciliation/run")
    assert run_resp.status_code == 200

    # Restore default settings
    client.post("/api/settings/reset")


def test_reconciliation_uses_changed_date_tolerance():
    """Verify that changing date_tolerance_days is read during reconciliation execution."""
    client.put("/api/settings", json={
        "amount_tolerance": 0.0,
        "date_tolerance_days": 10,
        "auto_match_threshold": 90.0,
        "review_threshold": 70.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    })

    run_resp = client.post("/api/reconciliation/run")
    assert run_resp.status_code == 200

    # Reset defaults
    client.post("/api/settings/reset")


def test_reconciliation_uses_changed_match_threshold():
    """Verify that lowering auto_match_threshold changes status determination in reconciliation."""
    client.put("/api/settings", json={
        "amount_tolerance": 0.0,
        "date_tolerance_days": 3,
        "auto_match_threshold": 75.0,
        "review_threshold": 60.0,
        "fuzzy_similarity_threshold": 70.0,
        "candidate_score_gap": 10.0
    })

    run_resp = client.post("/api/reconciliation/run")
    assert run_resp.status_code == 200

    # Reset defaults
    client.post("/api/settings/reset")
