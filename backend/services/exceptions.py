"""
Exception Detection & Classification Service
=============================================
Identifies, classifies, and manages multi-source reconciliation exceptions across 10 distinct discrepancy types.

Supported Exception Types:
1. AMOUNT_MISMATCH (HIGH)
2. MISSING_BANK_PAYMENT (HIGH)
3. MISSING_GATEWAY_PAYMENT (HIGH)
4. DUPLICATE_PAYMENT (CRITICAL)
5. AMBIGUOUS_MATCH (HIGH)
6. CUSTOMER_MISMATCH (MEDIUM)
7. REFERENCE_MISMATCH (LOW)
8. DATE_OUT_OF_RANGE (LOW)
9. CURRENCY_MISMATCH (CRITICAL)
10. POSSIBLE_GATEWAY_FEE (MEDIUM)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# In-memory store for generated exceptions
EXCEPTIONS_CACHE: Dict[str, Dict[str, Any]] = {}
EXCEPTION_COUNTER = 1

SUGGESTED_ACTIONS = {
    "AMOUNT_MISMATCH": "Verify partial payment, withholding tax (TDS), deduction, or incorrect invoice amount.",
    "MISSING_BANK_PAYMENT": "Check whether payment has settled or whether the bank statement feed is incomplete.",
    "MISSING_GATEWAY_PAYMENT": "Check payment gateway settlement report or gateway processing status.",
    "DUPLICATE_PAYMENT": "Verify duplicate settlement or repeated transaction before posting to ledger.",
    "AMBIGUOUS_MATCH": "Manual review required because multiple candidates have similar confidence scores.",
    "CUSTOMER_MISMATCH": "Verify customer entity relationship, subsidiary, or name abbreviation.",
    "REFERENCE_MISMATCH": "Verify reference ID typo or cross-check PO/invoice reference.",
    "DATE_OUT_OF_RANGE": "Verify delayed settlement window or late payment approval.",
    "CURRENCY_MISMATCH": "Verify cross-border foreign currency exchange rate and settlement currency.",
    "POSSIBLE_GATEWAY_FEE": "Verify gateway processing fee deduction against gross invoice amount."
}

SEVERITY_LEVELS = {
    "CURRENCY_MISMATCH": "CRITICAL",
    "DUPLICATE_PAYMENT": "CRITICAL",
    "AMOUNT_MISMATCH": "HIGH",
    "MISSING_BANK_PAYMENT": "HIGH",
    "MISSING_GATEWAY_PAYMENT": "HIGH",
    "AMBIGUOUS_MATCH": "HIGH",
    "CUSTOMER_MISMATCH": "MEDIUM",
    "POSSIBLE_GATEWAY_FEE": "MEDIUM",
    "REFERENCE_MISMATCH": "LOW",
    "DATE_OUT_OF_RANGE": "LOW"
}


def reset_exceptions_cache():
    """Reset exceptions in-memory cache."""
    global EXCEPTIONS_CACHE, EXCEPTION_COUNTER
    EXCEPTIONS_CACHE.clear()
    EXCEPTION_COUNTER = 1


def generate_exception_record(
    batch_id: str,
    invoice_id: str,
    exception_type: str,
    confidence_score: float,
    reason: str,
    bank_ids: List[str] = None,
    gateway_ids: List[str] = None,
    amount_diff: Optional[float] = None,
    pct_diff: Optional[float] = None,
    gross_amount: Optional[float] = None,
    fee: Optional[float] = None,
    net_amount: Optional[float] = None
) -> Dict[str, Any]:
    """Generates a structured exception record dict."""
    global EXCEPTION_COUNTER
    exc_id = f"EXC-{EXCEPTION_COUNTER:03d}"
    EXCEPTION_COUNTER += 1

    severity = SEVERITY_LEVELS.get(exception_type, "MEDIUM")
    suggested_action = SUGGESTED_ACTIONS.get(exception_type, "Investigate discrepancy.")

    record = {
        "exception_id": exc_id,
        "batch_id": batch_id,
        "invoice_id": invoice_id,
        "exception_type": exception_type,
        "severity": severity,
        "confidence_score": round(confidence_score, 2),
        "reason": reason,
        "suggested_action": suggested_action,
        "candidate_bank_transaction_ids": bank_ids or [],
        "candidate_gateway_payment_ids": gateway_ids or [],
        "amount_difference": round(amount_diff, 2) if amount_diff is not None else None,
        "percentage_difference": round(pct_diff, 2) if pct_diff is not None else None,
        "gross_amount": round(gross_amount, 2) if gross_amount is not None else None,
        "fee": round(fee, 2) if fee is not None else None,
        "net_amount": round(net_amount, 2) if net_amount is not None else None,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "OPEN"
    }

    EXCEPTIONS_CACHE[exc_id] = record
    return record


def get_all_exceptions(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    exception_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Returns all active exceptions from cache, with optional filtering."""
    results = list(EXCEPTIONS_CACHE.values())
    if status:
        results = [e for e in results if e["status"].upper() == status.upper()]
    if severity:
        results = [e for e in results if e["severity"].upper() == severity.upper()]
    if exception_type:
        results = [e for e in results if e["exception_type"].upper() == exception_type.upper()]
    return results


def get_exception_by_id(exception_id: str) -> Optional[Dict[str, Any]]:
    """Returns single exception record by ID."""
    return EXCEPTIONS_CACHE.get(exception_id)


def get_exceptions_summary() -> Dict[str, Any]:
    """Computes aggregated metrics across all active exceptions."""
    total = len(EXCEPTIONS_CACHE)
    open_count = sum(1 for e in EXCEPTIONS_CACHE.values() if e["status"] == "OPEN")

    by_severity = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }
    by_type: Dict[str, int] = {}

    for e in EXCEPTIONS_CACHE.values():
        sev = e["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1

        t = e["exception_type"]
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "total": total,
        "open": open_count,
        "by_severity": by_severity,
        "by_type": by_type
    }
