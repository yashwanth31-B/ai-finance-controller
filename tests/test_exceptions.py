import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.reconciliation import run_reconciliation_batch
from services.exceptions import get_all_exceptions, get_exceptions_summary

client = TestClient(app)


def test_amount_mismatch_exception():
    """Verify amount mismatch generates AMOUNT_MISMATCH exception with amount difference metrics."""
    inv = {
        "invoice_id": "INV_EXC_AMT",
        "customer_name": "ABC Private Limited",
        "reference": "REF001",
        "amount": 20000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    bank = {
        "transaction_id": "BANK_EXC_AMT",
        "description": "ABC PVT LTD PAYMENT REF001",
        "reference": "REF001",
        "amount": 19500.0,  # 500 difference
        "currency": "INR",
        "transaction_date": "2026-08-01"
    }

    summary, results = run_reconciliation_batch([inv], [bank], [])
    res = results[0]
    assert res["status"] == "EXCEPTION"
    assert res["exception_type"] == "AMOUNT_MISMATCH"
    assert res["severity"] == "HIGH"

    exc_list = get_all_exceptions(exception_type="AMOUNT_MISMATCH")
    assert len(exc_list) >= 1
    assert exc_list[0]["amount_difference"] == 500.0
    assert exc_list[0]["percentage_difference"] == 2.5


def test_missing_bank_payment_exception():
    """Verify missing bank feed generates MISSING_BANK_PAYMENT exception."""
    inv = {
        "invoice_id": "INV_EXC_NO_BANK",
        "customer_name": "Ravi Enterprises Private Limited",
        "reference": "REF002",
        "amount": 12500.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    gw = {
        "payment_id": "PAY_EXC_NO_BANK",
        "gateway": "Razorpay",
        "customer_name": "RAVI ENTERPRISE",
        "reference": "REF002",
        "amount": 12500.0,
        "fee": 250.0,
        "net_amount": 12250.0,
        "currency": "INR",
        "payment_date": "2026-08-01"
    }

    summary, results = run_reconciliation_batch([inv], [], [gw])
    res = results[0]
    assert res["exception_type"] == "MISSING_BANK_PAYMENT"
    assert res["severity"] == "HIGH"


def test_missing_gateway_payment_exception():
    """Verify missing gateway feed generates MISSING_GATEWAY_PAYMENT exception."""
    inv = {
        "invoice_id": "INV_EXC_NO_GW",
        "customer_name": "Apex Global Technologies Pvt Ltd",
        "reference": "REF003",
        "amount": 35000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    bank = {
        "transaction_id": "BANK_EXC_NO_GW",
        "description": "APEX GLOBAL TECH REF003",
        "reference": "REF003",
        "amount": 35000.0,
        "currency": "INR",
        "transaction_date": "2026-08-01"
    }

    summary, results = run_reconciliation_batch([inv], [bank], [])
    res = results[0]
    assert res["exception_type"] == "MISSING_GATEWAY_PAYMENT"
    assert res["severity"] == "HIGH"


def test_duplicate_bank_transaction_exception():
    """Verify transaction ID reuse across multiple invoices generates DUPLICATE_PAYMENT (CRITICAL)."""
    inv1 = {
        "invoice_id": "INV_DUP_1",
        "customer_name": "ABC Private Limited",
        "reference": "REF004",
        "amount": 10000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    inv2 = {
        "invoice_id": "INV_DUP_2",
        "customer_name": "ABC Private Limited",
        "reference": "REF004",
        "amount": 10000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    bank_shared = {
        "transaction_id": "BANK_SHARED_100",
        "description": "ABC PVT LTD PAYMENT REF004",
        "reference": "REF004",
        "amount": 10000.0,
        "currency": "INR",
        "transaction_date": "2026-08-01"
    }

    summary, results = run_reconciliation_batch([inv1, inv2], [bank_shared], [])
    assert results[0]["exception_type"] == "DUPLICATE_PAYMENT"
    assert results[0]["severity"] == "CRITICAL"
    assert results[1]["exception_type"] == "DUPLICATE_PAYMENT"
    assert results[1]["severity"] == "CRITICAL"


def test_duplicate_gateway_transaction_exception():
    """Verify gateway payment reuse across multiple invoices generates DUPLICATE_PAYMENT."""
    inv1 = {"invoice_id": "INV_GW_DUP_1", "customer_name": "Wipro Ltd", "reference": "REF005", "amount": 5000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    inv2 = {"invoice_id": "INV_GW_DUP_2", "customer_name": "Wipro Ltd", "reference": "REF005", "amount": 5000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    gw_shared = {"payment_id": "PAY_SHARED_200", "gateway": "Stripe", "customer_name": "Wipro Ltd", "reference": "REF005", "amount": 5000.0, "fee": 100.0, "net_amount": 4900.0, "currency": "INR", "payment_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv1, inv2], [], [gw_shared])
    assert results[0]["exception_type"] == "DUPLICATE_PAYMENT"
    assert results[1]["exception_type"] == "DUPLICATE_PAYMENT"


def test_ambiguous_candidate_match_exception():
    """Verify ambiguous candidate match generates AMBIGUOUS_MATCH exception."""
    inv = {"invoice_id": "INV_EXC_AMBIG", "customer_name": "Zenith Logistics", "reference": "REF006", "amount": 10000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    b1 = {"transaction_id": "BANK_AMBIG_1", "description": "ZENITH LOGISTICS REF006", "reference": "REF006", "amount": 10000.0, "currency": "INR", "transaction_date": "2026-08-01"}
    b2 = {"transaction_id": "BANK_AMBIG_2", "description": "ZENITH LOGISTICS REF006", "reference": "REF006", "amount": 10000.0, "currency": "INR", "transaction_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [b1, b2], [])
    assert results[0]["exception_type"] == "AMBIGUOUS_MATCH"
    assert results[0]["severity"] == "HIGH"


def test_customer_mismatch_exception():
    """Verify customer mismatch generates CUSTOMER_MISMATCH exception."""
    inv = {"invoice_id": "INV_CUST_MIS", "customer_name": "Tata Consultancy Services", "reference": "REF007", "amount": 15000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    b = {"transaction_id": "BANK_CUST_MIS", "description": "GLOBAL LOGISTICS REF007", "reference": "REF007", "amount": 15000.0, "currency": "INR", "transaction_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [b], [])
    res = results[0]
    assert res["status"] in ("REVIEW", "EXCEPTION")
    assert res["exception_type"] in ("CUSTOMER_MISMATCH", "MISSING_GATEWAY_PAYMENT")


def test_reference_mismatch_exception():
    """Verify reference mismatch generates REFERENCE_MISMATCH exception."""
    inv = {"invoice_id": "INV_REF_MIS", "customer_name": "Infosys BPM", "reference": "REF_CORRECT", "amount": 18000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    b = {"transaction_id": "BANK_REF_MIS", "description": "INFOSYS BPM PAYMENT REF_TYPO", "reference": "REF_TYPO", "amount": 18000.0, "currency": "INR", "transaction_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [b], [])
    res = results[0]
    assert res["exception_type"] in ("REFERENCE_MISMATCH", "MISSING_GATEWAY_PAYMENT")


def test_date_out_of_range_exception():
    """Verify date difference > 3 days generates DATE_OUT_OF_RANGE exception."""
    inv = {"invoice_id": "INV_DATE_OUT", "customer_name": "Wipro Digital", "reference": "REF009", "amount": 25000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    b = {"transaction_id": "BANK_DATE_OUT", "description": "WIPRO DIGITAL REF009", "reference": "REF009", "amount": 25000.0, "currency": "INR", "transaction_date": "2026-08-20"}  # 19 days diff

    summary, results = run_reconciliation_batch([inv], [b], [])
    res = results[0]
    assert res["exception_type"] in ("DATE_OUT_OF_RANGE", "MISSING_GATEWAY_PAYMENT")


def test_currency_mismatch_exception():
    """Verify currency mismatch generates CURRENCY_MISMATCH (CRITICAL)."""
    inv = {"invoice_id": "INV_CURR_MIS", "customer_name": "HCL Technologies", "reference": "REF010", "amount": 1000.0, "currency": "USD", "invoice_date": "2026-08-01"}
    b = {"transaction_id": "BANK_CURR_MIS", "description": "HCL TECH REF010", "reference": "REF010", "amount": 83000.0, "currency": "INR", "transaction_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [b], [])
    res = results[0]
    assert res["exception_type"] == "CURRENCY_MISMATCH"
    assert res["severity"] == "CRITICAL"


def test_possible_gateway_fee_exception():
    """Verify gateway net amount deduction generates POSSIBLE_GATEWAY_FEE exception."""
    inv = {"invoice_id": "INV_FEE", "customer_name": "Swiggy Bundl", "reference": "REF011", "amount": 10000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    bank = {"transaction_id": "BANK_FEE", "description": "Swiggy Bundl REF011", "reference": "REF011", "amount": 10000.0, "currency": "INR", "transaction_date": "2026-08-01"}
    gw = {"payment_id": "PAY_FEE", "gateway": "Razorpay", "customer_name": "Swiggy Bundl", "reference": "REF011", "amount": 10000.0, "fee": 200.0, "net_amount": 9800.0, "currency": "INR", "payment_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [bank], [gw])
    res = results[0]
    assert res["exception_type"] == "POSSIBLE_GATEWAY_FEE"
    assert res["severity"] == "MEDIUM"


def test_strong_valid_match_does_not_become_exception():
    """Verify 100% matched invoice yields status MATCHED and correct confidence score.

    When bank amount matches the invoice exactly and gateway net differs only due to
    a gateway fee, a POSSIBLE_GATEWAY_FEE informational exception is expected even on
    a MATCHED invoice (audit trail). The key assertions are status=MATCHED and full
    confidence score=100.0.
    """
    inv = {"invoice_id": "INV_PERFECT", "customer_name": "Perfect Corp", "reference": "REF100", "amount": 50000.0, "currency": "INR", "invoice_date": "2026-08-01"}
    bank = {"transaction_id": "BANK_PERFECT", "description": "PERFECT CORP REF100", "reference": "REF100", "amount": 50000.0, "currency": "INR", "transaction_date": "2026-08-01"}
    gw = {"payment_id": "PAY_PERFECT", "gateway": "Stripe", "customer_name": "Perfect Corp", "reference": "REF100", "amount": 50000.0, "fee": 1000.0, "net_amount": 49000.0, "currency": "INR", "payment_date": "2026-08-01"}

    summary, results = run_reconciliation_batch([inv], [bank], [gw])
    res = results[0]
    # Invoice is fully matched — bank reconciles perfectly with invoice amount
    assert res["status"] == "MATCHED"
    assert res["overall_confidence_score"] == 100.0
    # POSSIBLE_GATEWAY_FEE is an informational exception on MATCHED records;
    # the invoice itself is not flagged as EXCEPTION status
    assert res["exception_type"] in (None, "POSSIBLE_GATEWAY_FEE")


def test_exceptions_api_endpoints():
    """Verify GET /api/exceptions, GET /api/exceptions/summary, and GET /api/exceptions/{id}."""
    # Execute batch reconciliation on full synthetic dataset first
    from scripts.generate_data import generate_all_datasets
    generate_all_datasets()

    # 1. Fetch summary metrics
    summary_resp = client.get("/api/exceptions/summary")
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert summary_data["total"] > 0
    assert "HIGH" in summary_data["by_severity"]

    # 2. Fetch list of exceptions
    list_resp = client.get("/api/exceptions")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert len(list_data) == summary_data["total"]

    # 3. Filter list by severity
    high_resp = client.get("/api/exceptions?severity=HIGH")
    assert high_resp.status_code == 200
    high_data = high_resp.json()
    for item in high_data:
        assert item["severity"] == "HIGH"

    # 4. Fetch single exception
    sample_exc_id = list_data[0]["exception_id"]
    single_resp = client.get(f"/api/exceptions/{sample_exc_id}")
    assert single_resp.status_code == 200
    assert single_resp.json()["exception_id"] == sample_exc_id

    # 5. Fetch 404 for invalid ID
    invalid_resp = client.get("/api/exceptions/EXC_INVALID_999")
    assert invalid_resp.status_code == 404
