import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app

client = TestClient(app)


def test_invoice_specific_question():
    """Verify POST /api/assistant/query answers invoice exception question using actual data."""
    # Ensure a batch has run
    client.post("/api/reconciliation/run")

    response = client.post("/api/assistant/query", json={
        "question": "Why is INV091 an exception?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "INV091" in data["related_invoice_ids"]
    assert len(data["data_sources_used"]) > 0


def test_metrics_question():
    """Verify POST /api/assistant/query answers system match rate & performance questions."""
    response = client.post("/api/assistant/query", json={
        "question": "What is the current match rate?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "match rate" in data["answer"].lower() or "matched" in data["answer"].lower()


def test_duplicate_payment_question():
    """Verify POST /api/assistant/query answers duplicate payment questions."""
    response = client.post("/api/assistant/query", json={
        "question": "Show all duplicate payments."
    })
    assert response.status_code == 200
    data = response.json()
    assert "duplicate" in data["answer"].lower()


def test_unknown_question_fallback():
    """Verify POST /api/assistant/query handles unknown out-of-domain questions with fallback message."""
    response = client.post("/api/assistant/query", json={
        "question": "What is the weather in Tokyo?"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "I cannot determine that from the current reconciliation data."
