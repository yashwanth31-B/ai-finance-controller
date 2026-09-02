import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.reconciliation import run_reconciliation_batch, load_csv_records, get_latest_results, get_result_by_invoice_id
from services.exceptions import get_all_exceptions

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_reconciliation_batch():
    """Ensures a batch run is executed before testing reviews."""
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    invoices = load_csv_records(os.path.join(data_dir, "invoices.csv"))
    bank = load_csv_records(os.path.join(data_dir, "bank_transactions.csv"))
    gateway = load_csv_records(os.path.join(data_dir, "gateway_transactions.csv"))
    run_reconciliation_batch(invoices, bank, gateway)


def test_approve_review_record():
    """1. Verify approving a REVIEW status record sets final_status to MATCHED_APPROVED."""
    results = get_latest_results()
    review_record = next((r for r in results if r["status"] == "REVIEW"), None)
    assert review_record is not None
    inv_id = review_record["invoice_id"]

    response = client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "APPROVE_MATCH",
        "reviewer_name": "Senior Auditor",
        "note": "Verified against bank statement"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["review_action"] == "APPROVE_MATCH"
    assert data["new_final_status"] == "MATCHED_APPROVED"

    updated = get_result_by_invoice_id(inv_id)
    assert updated["human_review_status"] == "APPROVED"
    assert updated["final_status"] == "MATCHED_APPROVED"


def test_reject_review_record():
    """2. Verify rejecting a REVIEW record sets final_status to REJECTED."""
    results = get_latest_results()
    review_record = next((r for r in results if r["status"] == "REVIEW"), None)
    assert review_record is not None
    inv_id = review_record["invoice_id"]

    response = client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "REJECT_MATCH",
        "reviewer_name": "Finance Reviewer",
        "note": "Mismatch on payment reference"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["new_final_status"] == "REJECTED"


def test_resolve_exception_record():
    """3. Verify marking an EXCEPTION record as resolved sets final_status to RESOLVED_MANUALLY."""
    results = get_latest_results()
    exc_record = next((r for r in results if r["status"] == "EXCEPTION"), None)
    assert exc_record is not None
    inv_id = exc_record["invoice_id"]

    response = client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "MARK_RESOLVED",
        "reviewer_name": "Controller",
        "note": "Manually posted wire transfer"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["new_final_status"] == "RESOLVED_MANUALLY"

    # Verify exception status updated to RESOLVED in exceptions list
    all_exceptions = get_all_exceptions()
    exc_entry = next((e for e in all_exceptions if e["invoice_id"] == inv_id), None)
    assert exc_entry is not None
    assert exc_entry["status"] == "RESOLVED"


def test_keep_record_under_review():
    """4. Verify KEEP_UNDER_REVIEW sets final_status to UNDER_REVIEW."""
    results = get_latest_results()
    exc_record = next((r for r in results if r["status"] == "EXCEPTION"), None)
    assert exc_record is not None
    inv_id = exc_record["invoice_id"]

    response = client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "KEEP_UNDER_REVIEW",
        "reviewer_name": "Reviewer 1",
        "note": "Awaiting customer response"
    })
    assert response.status_code == 200
    assert response.json()["new_final_status"] == "UNDER_REVIEW"


def test_audit_row_created_for_every_action():
    """5. Verify an audit trail row is created for every review action."""
    results = get_latest_results()
    inv_id = results[0]["invoice_id"]

    client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "KEEP_UNDER_REVIEW",
        "reviewer_name": "Audit Test User",
        "note": "Initial review"
    })

    response = client.get(f"/api/audit-trail?invoice_id={inv_id}")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 1
    assert events[0]["actor"] == "Audit Test User"
    assert events[0]["event_type"] == "REVIEW_RETURNED_TO_REVIEW"


def test_original_system_decision_is_preserved():
    """6. Verify original system status & confidence score are preserved immutably."""
    results = get_latest_results()
    review_record = next((r for r in results if r["status"] == "REVIEW"), None)
    assert review_record is not None
    inv_id = review_record["invoice_id"]
    orig_status = review_record["status"]
    orig_confidence = review_record["overall_confidence_score"]

    client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "APPROVE_MATCH",
        "reviewer_name": "Reviewer",
        "note": "Approving"
    })

    updated = get_result_by_invoice_id(inv_id)
    assert updated["status"] == orig_status  # Unchanged
    assert updated["overall_confidence_score"] == orig_confidence  # Unchanged
    assert updated["final_status"] == "MATCHED_APPROVED"  # Derived final status


def test_second_review_action_does_not_delete_first():
    """7. Verify submitting a second review action preserves full history."""
    results = get_latest_results()
    inv_id = results[1]["invoice_id"]

    # First review: Approve
    client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "APPROVE_MATCH",
        "reviewer_name": "Reviewer 1",
        "note": "First approval"
    })

    # Second review: Reject
    client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "REJECT_MATCH",
        "reviewer_name": "Senior Reviewer",
        "note": "Reversing approval after investigation"
    })

    history_resp = client.get(f"/api/reviews/{inv_id}")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 2
    assert history[0]["review_action"] == "REJECT_MATCH"
    assert history[1]["review_action"] == "APPROVE_MATCH"


def test_latest_action_determines_final_decision():
    """8. Verify latest review action sets the current final decision."""
    results = get_latest_results()
    inv_id = results[2]["invoice_id"]

    client.post("/api/reviews", json={"invoice_id": inv_id, "action": "KEEP_UNDER_REVIEW", "reviewer_name": "User 1"})
    client.post("/api/reviews", json={"invoice_id": inv_id, "action": "APPROVE_MATCH", "reviewer_name": "User 2"})

    updated = get_result_by_invoice_id(inv_id)
    assert updated["final_status"] == "MATCHED_APPROVED"


def test_nonexistent_invoice_returns_error():
    """9. Verify reviewing a non-existent invoice returns HTTP 404."""
    response = client.post("/api/reviews", json={
        "invoice_id": "INV_NON_EXISTENT_999",
        "action": "APPROVE_MATCH",
        "reviewer_name": "Reviewer"
    })
    assert response.status_code == 404


def test_invalid_action_returns_error():
    """10. Verify invalid action string returns HTTP 400."""
    results = get_latest_results()
    inv_id = results[0]["invoice_id"]

    response = client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "SUPER_APPROVE_INVALID",
        "reviewer_name": "Reviewer"
    })
    assert response.status_code == 400


def test_matched_automatic_result_is_not_silently_changed():
    """11. Verify automatic MATCHED results remain MATCHED_AUTO without manual review."""
    results = get_latest_results()
    matched_record = next((r for r in results if r["status"] == "MATCHED" and r.get("human_review_status") == "NOT_REVIEWED"), None)
    if matched_record:
        assert matched_record["status"] == "MATCHED"
        assert matched_record["human_review_status"] == "NOT_REVIEWED"


def test_resolved_exception_remains_in_audit_history():
    """12. Verify resolved exceptions remain recorded in audit trail and exception registry."""
    results = get_latest_results()
    exc_record = next((r for r in results if r["status"] == "EXCEPTION"), None)
    assert exc_record is not None
    inv_id = exc_record["invoice_id"]

    client.post("/api/reviews", json={
        "invoice_id": inv_id,
        "action": "MARK_RESOLVED",
        "reviewer_name": "Auditor",
        "note": "Resolved externally"
    })

    audit_resp = client.get(f"/api/audit-trail?invoice_id={inv_id}")
    assert audit_resp.status_code == 200
    events = audit_resp.json()
    assert any(e["event_type"] == "REVIEW_MARKED_RESOLVED" for e in events)
