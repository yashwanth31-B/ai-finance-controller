import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.normalization import normalize_record
from services.scoring import score_candidate
from services.reconciliation import run_reconciliation_batch

client = TestClient(app)


def test_exact_invoice_bank_match():
    """Verify exact invoice-bank match yields total score 100 and MATCHED status."""
    inv = {
        "invoice_id": "INV001",
        "customer_name": "ABC Private Limited",
        "reference": "REF001",
        "amount": 12500.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    bank = {
        "transaction_id": "BANK001",
        "description": "ABC PVT LTD PAYMENT REF001",
        "reference": "REF001",
        "amount": 12500.0,
        "currency": "INR",
        "transaction_date": "2026-08-01"
    }

    inv_norm = normalize_record(inv)["normalized"]
    bank_norm = normalize_record(bank)["normalized"]

    score_res = score_candidate(inv_norm, bank_norm)
    assert score_res["total_score"] == 100.0
    assert set(score_res["matched_fields"]) == {"amount", "customer_name", "reference", "date", "currency"}


def test_exact_invoice_gateway_match():
    """Verify exact invoice-gateway match yields total score 100."""
    inv = {
        "invoice_id": "INV001",
        "customer_name": "Ravi Enterprises Private Limited",
        "reference": "REF001",
        "amount": 24000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    gw = {
        "payment_id": "PAY001",
        "gateway": "Razorpay",
        "customer_name": "RAVI ENTERPRISE",
        "reference": "REF001",
        "amount": 24000.0,
        "fee": 480.0,
        "net_amount": 23520.0,
        "currency": "INR",
        "payment_date": "2026-08-01"
    }

    inv_norm = normalize_record(inv)["normalized"]
    gw_norm = normalize_record(gw)["normalized"]

    score_res = score_candidate(inv_norm, gw_norm)
    assert score_res["total_score"] == 100.0
    assert "amount" in score_res["matched_fields"]
    assert "customer_name" in score_res["matched_fields"]


def test_matching_normalized_company_names():
    """Verify company name normalization scores 20 points across legal suffix variations."""
    inv_norm = normalize_record({"customer_name": "Apex Global Technologies Pvt Ltd"})["normalized"]
    cand_norm = normalize_record({"customer_name": "APEX GLOBAL TECHNOLOGIES INC"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["customer_name_score"] == 20.0
    assert "customer_name" in score_res["matched_fields"]


def test_matching_normalized_references():
    """Verify reference normalization scores 20 points across casing/punctuation variations."""
    inv_norm = normalize_record({"reference": "INV-2026-001"})["normalized"]
    cand_norm = normalize_record({"reference": "inv.2026.001"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["reference_score"] == 20.0
    assert "reference" in score_res["matched_fields"]


def test_one_day_date_difference():
    """Verify 1-day date difference yields 13 points out of 15 for date proximity."""
    inv_norm = normalize_record({"date": "2026-08-01"})["normalized"]
    cand_norm = normalize_record({"date": "2026-08-02"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["date_score"] == 13.0
    assert "date" in score_res["matched_fields"]


def test_amount_mismatch():
    """Verify amount mismatch scores 0 points out of 40 for amount."""
    inv_norm = normalize_record({"amount": 20000.0})["normalized"]
    cand_norm = normalize_record({"amount": 19500.0})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["amount_score"] == 0.0
    assert "amount" in score_res["mismatched_fields"]


def test_currency_mismatch():
    """Verify currency mismatch scores 0 points out of 5 for currency."""
    inv_norm = normalize_record({"currency": "USD"})["normalized"]
    cand_norm = normalize_record({"currency": "INR"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["currency_score"] == 0.0
    assert "currency" in score_res["mismatched_fields"]


def test_low_confidence_record():
    """Verify low confidence transaction yields EXCEPTION status."""
    invoices = [{
        "invoice_id": "INV_LOW",
        "customer_name": "Unique Company XYZ",
        "amount": "99999.00",
        "currency": "INR",
        "invoice_date": "2026-08-01",
        "reference": "REF999"
    }]
    bank_txns = [{
        "transaction_id": "BANK_OTHER",
        "description": "Completely Different Payment",
        "amount": "100.00",
        "currency": "EUR",
        "transaction_date": "2026-08-25",
        "reference": "REF000"
    }]

    summary, results = run_reconciliation_batch(invoices, bank_txns, [])
    assert summary["exceptions"] == 1
    assert results[0]["status"] == "EXCEPTION"
    assert results[0]["overall_confidence_score"] < 70.0


def test_ambiguous_candidates():
    """Verify multiple top candidates with identical/near scores flag REVIEW with reason."""
    invoices = [{
        "invoice_id": "INV_AMBIGUOUS",
        "customer_name": "ABC Private Limited",
        "amount": "10000.00",
        "currency": "INR",
        "invoice_date": "2026-08-01",
        "reference": "REF100"
    }]
    bank_txns = [
        {
            "transaction_id": "BANK_CANDIDATE_1",
            "description": "ABC PVT LTD PAYMENT REF100",
            "amount": "10000.00",
            "currency": "INR",
            "transaction_date": "2026-08-01",
            "reference": "REF100"
        },
        {
            "transaction_id": "BANK_CANDIDATE_2",
            "description": "ABC PVT LTD PAYMENT REF100",
            "amount": "10000.00",
            "currency": "INR",
            "transaction_date": "2026-08-01",
            "reference": "REF100"
        }
    ]

    summary, results = run_reconciliation_batch(invoices, bank_txns, [])
    assert results[0]["status"] == "REVIEW"
    assert "Multiple possible matches" in results[0]["explanation"]


def test_record_with_no_candidate():
    """Verify invoice with empty bank and gateway feeds resolves to EXCEPTION."""
    invoices = [{
        "invoice_id": "INV_NO_CANDIDATE",
        "customer_name": "Isolated Firm",
        "amount": "5000.00",
        "currency": "INR",
        "invoice_date": "2026-08-01",
        "reference": "REF500"
    }]

    summary, results = run_reconciliation_batch(invoices, [], [])
    assert summary["exceptions"] == 1
    assert results[0]["status"] == "EXCEPTION"
    assert results[0]["selected_bank_transaction_id"] is None
    assert results[0]["selected_gateway_payment_id"] is None


def test_reconciliation_api_endpoints():
    """Verify POST /api/reconciliation/run and GET /api/reconciliation/results endpoints."""
    # 1. Run batch reconciliation
    run_resp = client.post("/api/reconciliation/run")
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["total_records"] >= 100
    assert run_data["results_available"] is True

    # 2. Get all results
    results_resp = client.get("/api/reconciliation/results")
    assert results_resp.status_code == 200
    results_data = results_resp.json()
    assert len(results_data) == run_data["total_records"]

    # 3. Get single invoice result
    sample_inv_id = results_data[0]["invoice_id"]
    single_resp = client.get(f"/api/reconciliation/results/{sample_inv_id}")
    assert single_resp.status_code == 200
    single_data = single_resp.json()
    assert single_data["invoice_id"] == sample_inv_id

    # 4. Get 404 for invalid invoice id
    invalid_resp = client.get("/api/reconciliation/results/INV_NON_EXISTENT_999")
    assert invalid_resp.status_code == 404
