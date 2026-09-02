import os
import sys
import pytest

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from services.normalization import (
    normalize_company_name,
    normalize_reference,
    normalize_amount,
    normalize_date,
    normalize_currency,
    normalize_record
)


def test_company_name_variations():
    """Verify company legal suffix stripping, casing, punctuation, and synonym standardization."""
    variations = [
        "ABC Private Limited",
        "ABC Pvt Ltd",
        "ABC PVT. LTD.",
        "abc private ltd",
        "ABC Pvt. Ltd."
    ]
    normalized_results = [normalize_company_name(name) for name in variations]
    assert len(set(normalized_results)) == 1
    assert normalized_results[0] == "abc"

    ravi_variations = [
        "Ravi Enterprises",
        "RAVI ENTERPRISE",
        "Ravi Enterprises Pvt Ltd",
        "Ravi Enterprise Private Limited"
    ]
    ravi_results = [normalize_company_name(name) for name in ravi_variations]
    assert len(set(ravi_results)) == 1
    assert ravi_results[0] == "ravi enterprises"


def test_company_name_distinction():
    """Verify normalization does NOT make distinct companies with different core names equal."""
    comp1 = normalize_company_name("ABC Technologies Private Limited")
    comp2 = normalize_company_name("ABC Logistics Private Limited")
    assert comp1 != comp2
    assert comp1 == "abc technologies"
    assert comp2 == "abc logistics"


def test_reference_normalization():
    """Verify reference normalization handles case, spaces, hyphens, and punctuation."""
    ref_variations = ["INV-001", "inv001", "INV 001", "INV-001.", "inv.001"]
    for ref in ref_variations:
        assert normalize_reference(ref) == "INV001"


def test_amount_normalization():
    """Verify numeric string parsing, currency symbol removal, and float formatting."""
    assert normalize_amount("₹12,500") == 12500.0
    assert normalize_amount("12500") == 12500.0
    assert normalize_amount("12,500.00") == 12500.0
    assert normalize_amount("$12,500.50") == 12500.50
    assert normalize_amount(12500) == 12500.0
    assert normalize_amount(12500.75) == 12500.75


def test_amount_invalid_values():
    """Verify invalid amount strings and empty inputs raise ValueError."""
    invalid_inputs = ["abc", "", None, "-", "12.34.56"]
    for val in invalid_inputs:
        with pytest.raises(ValueError):
            normalize_amount(val)


def test_date_normalization():
    """Verify date parsing across common standard formats into ISO format."""
    assert normalize_date("2026-08-01") == "2026-08-01"
    assert normalize_date("01-08-2026") == "2026-08-01"
    assert normalize_date("01/08/2026") == "2026-08-01"
    assert normalize_date("2026/08/01") == "2026-08-01"
    assert normalize_date("01.08.2026") == "2026-08-01"


def test_date_invalid_values():
    """Verify invalid date strings or unparseable dates raise ValueError."""
    invalid_dates = ["invalid-date", "2026-13-45", "", None, "99/99/9999"]
    for d in invalid_dates:
        with pytest.raises(ValueError):
            normalize_date(d)


def test_currency_normalization():
    """Verify 3-letter currency code normalization and case standardization."""
    assert normalize_currency("inr") == "INR"
    assert normalize_currency("INR") == "INR"
    assert normalize_currency("  usd ") == "USD"


def test_currency_invalid_values():
    """Verify invalid currency strings raise ValueError."""
    invalid_currencies = ["US", "RUPEES", "", None, "1234"]
    for c in invalid_currencies:
        with pytest.raises(ValueError):
            normalize_currency(c)


def test_normalize_record_full():
    """Verify normalize_record returns both original raw input and normalized payload."""
    raw_record = {
        "invoice_id": "INV001",
        "customer_name": "ABC Private Limited",
        "reference": "INV-001",
        "amount": "₹12,500.00",
        "currency": "inr",
        "invoice_date": "01-08-2026"
    }

    result = normalize_record(raw_record)

    # Check original remains untouched
    assert result["original"] == raw_record

    # Check normalized structure
    assert result["normalized"]["customer_name"] == "abc"
    assert result["normalized"]["reference"] == "INV001"
    assert result["normalized"]["amount"] == 12500.0
    assert result["normalized"]["currency"] == "INR"
    assert result["normalized"]["date"] == "2026-08-01"
