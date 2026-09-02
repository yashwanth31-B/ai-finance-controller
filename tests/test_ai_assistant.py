import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.reconciliation import run_reconciliation_batch, load_csv_records, get_latest_results

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_reconciliation_batch():
    """Ensures a batch run is executed before testing AI assistant."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    invoices = load_csv_records(os.path.join(data_dir, "invoices.csv"))
    bank = load_csv_records(os.path.join(data_dir, "bank_transactions.csv"))
    gateway = load_csv_records(os.path.join(data_dir, "gateway_transactions.csv"))
    run_reconciliation_batch(invoices, bank, gateway)


def test_ai_analyze_valid_invoice_id():
    """1. Verify POST /api/ai/analyze-exception returns structured analysis for valid invoice ID."""
    results = get_latest_results()
    exc_record = next((r for r in results if r["status"] == "EXCEPTION"), None)
    assert exc_record is not None
    inv_id = exc_record["invoice_id"]

    response = client.post("/api/ai/analyze-exception", json={"invoice_id": inv_id})
    assert response.status_code == 200
    data = response.json()
    assert data["invoice_id"] == inv_id
    assert "root_cause_summary" in data
    assert "recommended_action" in data
    assert "confidence_score" in data
    assert data["recommended_action"] in ("APPROVE_MATCH", "REJECT_MATCH", "MARK_RESOLVED", "KEEP_UNDER_REVIEW")


def test_ai_heuristic_fallback_when_no_api_key():
    """2. Verify heuristic AI engine operates seamlessly when AI_API_KEY is not set."""
    results = get_latest_results()
    inv_id = results[0]["invoice_id"]

    response = client.post("/api/ai/analyze-exception", json={"invoice_id": inv_id})
    assert response.status_code == 200
    data = response.json()
    assert "Heuristic Financial AI Engine" in data["ai_provider_used"]


def test_ai_analyze_nonexistent_invoice():
    """3. Verify error 404 when invoice ID is not found."""
    response = client.post("/api/ai/analyze-exception", json={"invoice_id": "INV_NOT_EXIST_999"})
    assert response.status_code == 404


def test_ai_analyze_missing_payload():
    """4. Verify error 400 when both invoice_id and exception_id are missing."""
    response = client.post("/api/ai/analyze-exception", json={})
    assert response.status_code == 400
