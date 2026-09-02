"""
Deterministic Candidate Scoring Engine
=======================================
Computes a match score (0 to 100 points) between a normalized invoice and a candidate record
(Bank transaction or Payment Gateway payment) based on exact normalized field criteria.

Scoring Rules:
- Amount match: 40 points (exact normalized amount match)
- Customer Name match: 20 points (exact normalized company name match)
- Reference match: 20 points (exact normalized reference ID match)
- Date proximity: 15 points (0 days = 15, 1 day = 13, 2 days = 10, 3 days = 7, >3 days = 0)
- Currency match: 5 points (exact normalized 3-letter currency code match)
Total: 100 points max
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple


def calculate_date_difference(date_str1: str, date_str2: str) -> int:
    """Calculate absolute difference in days between two ISO date strings (YYYY-MM-DD)."""
    if not date_str1 or not date_str2:
        return 999
    try:
        d1 = datetime.strptime(date_str1, "%Y-%m-%d").date()
        d2 = datetime.strptime(date_str2, "%Y-%m-%d").date()
        return abs((d1 - d2).days)
    except (ValueError, TypeError):
        return 999


def score_candidate(invoice_norm: Dict[str, Any], candidate_norm: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes candidate match score against an invoice using normalized fields.
    Returns score breakdown, total score (0 to 100), matched fields, and mismatched fields.
    """
    matched_fields: List[str] = []
    mismatched_fields: List[str] = []

    # 1. Amount Match (40 pts)
    inv_amount = invoice_norm.get("amount")
    cand_amount = candidate_norm.get("amount")
    amount_score = 0.0

    if inv_amount is not None and cand_amount is not None and abs(inv_amount - cand_amount) < 0.001:
        amount_score = 40.0
        matched_fields.append("amount")
    else:
        mismatched_fields.append("amount")

    # 2. Customer Name Match (20 pts)
    inv_name = invoice_norm.get("customer_name", "")
    cand_name = candidate_norm.get("customer_name", "")
    customer_score = 0.0

    if inv_name and cand_name and inv_name == cand_name:
        customer_score = 20.0
        matched_fields.append("customer_name")
    else:
        mismatched_fields.append("customer_name")

    # 3. Reference Match (20 pts)
    inv_ref = invoice_norm.get("reference", "")
    cand_ref = candidate_norm.get("reference", "")
    ref_score = 0.0

    if inv_ref and cand_ref and inv_ref == cand_ref:
        ref_score = 20.0
        matched_fields.append("reference")
    else:
        mismatched_fields.append("reference")

    # 4. Date Proximity Match (15 pts)
    inv_date = invoice_norm.get("date")
    cand_date = candidate_norm.get("date")
    date_diff = calculate_date_difference(inv_date, cand_date)
    date_score = 0.0

    if date_diff == 0:
        date_score = 15.0
        matched_fields.append("date")
    elif date_diff == 1:
        date_score = 13.0
        matched_fields.append("date")
    elif date_diff == 2:
        date_score = 10.0
        matched_fields.append("date")
    elif date_diff == 3:
        date_score = 7.0
        matched_fields.append("date")
    else:
        mismatched_fields.append("date")

    # 5. Currency Match (5 pts)
    inv_curr = invoice_norm.get("currency", "")
    cand_curr = candidate_norm.get("currency", "")
    currency_score = 0.0

    if inv_curr and cand_curr and inv_curr == cand_curr:
        currency_score = 5.0
        matched_fields.append("currency")
    else:
        mismatched_fields.append("currency")

    total_score = amount_score + customer_score + ref_score + date_score + currency_score

    return {
        "total_score": round(total_score, 2),
        "amount_score": amount_score,
        "customer_name_score": customer_score,
        "reference_score": ref_score,
        "date_score": date_score,
        "currency_score": currency_score,
        "matched_fields": matched_fields,
        "mismatched_fields": mismatched_fields
    }
