import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.fuzzy_matching import (
    fuzzy_company_name_similarity,
    fuzzy_description_similarity,
    fuzzy_reference_similarity
)
from services.normalization import normalize_record
from services.scoring import score_candidate
from services.reconciliation import run_reconciliation_batch

client = TestClient(app_module := __import__("main").app)


def test_exact_company_name_match():
    """Verify exact company name match scores 100% similarity."""
    sim = fuzzy_company_name_similarity("ABC Technologies Private Limited", "ABC Technologies Private Limited")
    assert sim == 100.0


def test_normalized_company_name_match():
    """Verify normalized company name match resolves legal suffixes cleanly."""
    n1 = normalize_record({"customer_name": "ABC Private Limited"})["normalized"]["customer_name"]
    n2 = normalize_record({"customer_name": "ABC PVT LTD"})["normalized"]["customer_name"]
    assert n1 == n2 == "abc"
    sim = fuzzy_company_name_similarity(n1, n2)
    assert sim == 100.0


def test_strong_fuzzy_match():
    """Verify strong fuzzy match for abbreviation/minor spelling differences yields score 80-100."""
    sim = fuzzy_company_name_similarity("ABC Technologies", "ABC Tech")
    assert 80.0 <= sim <= 100.0


def test_weak_fuzzy_match():
    """Verify weak fuzzy match for heavily distinct strings yields score < 70."""
    sim = fuzzy_company_name_similarity("ABC Technologies", "Global Freight Enterprises")
    assert sim < 70.0


def test_unrelated_company_names_distinction():
    """Verify unrelated companies sharing prefix (ABC Technologies vs ABC Logistics) score < 70."""
    n1 = normalize_record({"customer_name": "ABC Technologies"})["normalized"]["customer_name"]
    n2 = normalize_record({"customer_name": "ABC Logistics"})["normalized"]["customer_name"]
    sim = fuzzy_company_name_similarity(n1, n2)
    assert sim < 70.0, f"Expected similarity < 70, got {sim}"


def test_bank_description_similarity():
    """Verify customer name matches embedded text in bank feed descriptions."""
    sim = fuzzy_description_similarity("ABC Technologies", "NEFT CR ABC TECH PAYMENT INV001")
    assert sim >= 70.0


def test_fuzzy_match_with_exact_amount():
    """Verify fuzzy name match combined with exact amount yields high confidence match (FUZZY)."""
    inv = {
        "invoice_id": "INV_FUZZY_1",
        "customer_name": "Apex Global Technologies Pvt Ltd",
        "reference": "REF888",
        "amount": 54000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    gw = {
        "payment_id": "PAY888",
        "gateway": "Razorpay",
        "customer_name": "APEX GLOBL TECH",  # Typo in GLOBL triggers fuzzy match
        "reference": "REF888",
        "amount": 54000.0,
        "fee": 1080.0,
        "net_amount": 52920.0,
        "currency": "INR",
        "payment_date": "2026-08-01"
    }

    inv_norm = normalize_record(inv)["normalized"]
    gw_norm = normalize_record(gw)["normalized"]

    score_res = score_candidate(inv_norm, gw_norm, gw)
    assert score_res["total_score"] >= 90.0
    assert score_res["matching_method"] == "FUZZY"


def test_fuzzy_match_with_amount_mismatch():
    """Verify financial control: high fuzzy name score cannot override amount mismatch."""
    inv = {
        "invoice_id": "INV_AMT_MISMATCH",
        "customer_name": "Apex Global Technologies Pvt Ltd",
        "reference": "REF888",
        "amount": 54000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01"
    }
    gw = {
        "payment_id": "PAY888",
        "gateway": "Razorpay",
        "customer_name": "APEX GLOBAL TECH",
        "reference": "REF888",
        "amount": 40000.0,  # 14,000 difference
        "currency": "INR",
        "payment_date": "2026-08-01"
    }

    summary, results = run_reconciliation_batch([inv], [], [gw])
    res = results[0]
    # Total score lost 40 pts for amount, max possible is 60 -> EXCEPTION (< 70)
    assert res["status"] == "EXCEPTION"
    assert "amount" in res["mismatched_fields"]


def test_ambiguous_candidates_detection():
    """Verify ambiguous candidates with score gap < 5.0 are flagged for REVIEW with AMBIGUOUS matching_method."""
    inv = {
        "invoice_id": "INV_AMBIG",
        "customer_name": "Zenith Logistics Solutions Limited",
        "amount": 62000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01",
        "reference": "REF777"
    }
    bank1 = {
        "transaction_id": "BANK777_A",
        "description": "ZENITH LOGISTICS SOLN PAYMENT REF777",
        "amount": 62000.0,
        "currency": "INR",
        "transaction_date": "2026-08-01",
        "reference": "REF777"
    }
    bank2 = {
        "transaction_id": "BANK777_B",
        "description": "ZENITH LOGISTICS SOLN PAYMENT REF777",
        "amount": 62000.0,
        "currency": "INR",
        "transaction_date": "2026-08-01",
        "reference": "REF777"
    }

    summary, results = run_reconciliation_batch([inv], [bank1, bank2], [])
    res = results[0]
    assert res["status"] == "REVIEW"
    assert res["matching_method"] == "AMBIGUOUS"
    assert res["candidate_score_gap"] < 5.0


def test_similar_company_names_different_amounts():
    """Verify similar company names across different amount transactions do NOT match."""
    inv = {
        "invoice_id": "INV_DIFF_AMT",
        "customer_name": "Tata Consultancy Services Limited",
        "amount": 150000.0,
        "currency": "INR",
        "invoice_date": "2026-08-01",
        "reference": "REF999"
    }
    bank = {
        "transaction_id": "BANK999",
        "description": "TCS LTD PAYMENT REF999",
        "amount": 5000.0,  # 100,000 difference!
        "currency": "INR",
        "transaction_date": "2026-08-01",
        "reference": "REF999"
    }

    summary, results = run_reconciliation_batch([inv], [bank], [])
    assert results[0]["status"] == "EXCEPTION"
    assert results[0]["overall_confidence_score"] < 70.0


def test_reference_formatting_differences():
    """Verify minor reference formatting differences score conservative fuzzy points."""
    sim = fuzzy_reference_similarity("INV-2026-001", "INV-2026-001A")
    assert sim >= 90.0

    inv_norm = normalize_record({"reference": "INV-2026-001"})["normalized"]
    cand_norm = normalize_record({"reference": "INV-2026-001A"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["reference_score"] == 15.0


def test_clearly_different_references():
    """Verify clearly different references score 0 points."""
    sim = fuzzy_reference_similarity("REF001", "REF999")
    assert sim == 0.0

    inv_norm = normalize_record({"reference": "REF001"})["normalized"]
    cand_norm = normalize_record({"reference": "REF999"})["normalized"]

    score_res = score_candidate(inv_norm, cand_norm)
    assert score_res["reference_score"] == 0.0
