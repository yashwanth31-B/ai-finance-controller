"""
Deterministic & Fuzzy Candidate Scoring Engine
===============================================
Computes a match score (0 to 100 points) between a normalized invoice and a candidate record
(Bank transaction or Payment Gateway payment) combining exact normalized criteria and RapidFuzz fuzzy matching.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from services.fuzzy_matching import (
    fuzzy_company_name_similarity,
    fuzzy_description_similarity,
    fuzzy_reference_similarity
)


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


def score_candidate(
    invoice_norm: Dict[str, Any],
    candidate_norm: Dict[str, Any],
    raw_candidate: Dict[str, Any] = None,
    settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes candidate match score against an invoice using normalized fields, RapidFuzz matching,
    and configured system tolerances/thresholds.
    """
    matched_fields: List[str] = []
    mismatched_fields: List[str] = []
    used_fuzzy = False

    amount_tolerance = float(settings.get("amount_tolerance", 0.0)) if settings else 0.0
    date_tolerance_days = int(settings.get("date_tolerance_days", 3)) if settings else 3
    fuzzy_similarity_threshold = float(settings.get("fuzzy_similarity_threshold", 70.0)) if settings else 70.0

    # 1. Amount Match (40 pts)
    inv_amount = invoice_norm.get("amount")
    cand_amount = candidate_norm.get("amount")
    amount_score = 0.0

    if inv_amount is not None and cand_amount is not None and abs(inv_amount - cand_amount) <= (amount_tolerance + 1e-6):
        amount_score = 40.0
        matched_fields.append("amount")
    else:
        mismatched_fields.append("amount")

    # 2. Customer Name Match (20 pts max)
    inv_name = invoice_norm.get("customer_name", "")
    cand_name = candidate_norm.get("customer_name", "")
    cand_desc = str(raw_candidate.get("description", "")) if raw_candidate else ""

    fuzzy_customer_score = fuzzy_company_name_similarity(inv_name, cand_name)
    desc_similarity = fuzzy_description_similarity(inv_name, cand_desc) if cand_desc else 0.0

    best_name_sim = max(fuzzy_customer_score, desc_similarity)
    customer_score = 0.0

    if inv_name and cand_name and inv_name == cand_name:
        customer_score = 20.0
        fuzzy_customer_score = 100.0
        matched_fields.append("customer_name")
    elif best_name_sim >= fuzzy_similarity_threshold:
        used_fuzzy = True
        if best_name_sim >= 90.0:
            customer_score = 18.0
        elif best_name_sim >= 80.0:
            customer_score = 15.0
        else:
            customer_score = 10.0
        matched_fields.append("customer_name")
    else:
        mismatched_fields.append("customer_name")

    # 3. Reference Match (20 pts max)
    inv_ref = invoice_norm.get("reference", "")
    cand_ref = candidate_norm.get("reference", "")
    ref_score = 0.0

    fuzzy_ref_score = 0.0
    if inv_ref and cand_ref:
        if inv_ref == cand_ref:
            ref_score = 20.0
            matched_fields.append("reference")
        else:
            fuzzy_ref_score = fuzzy_reference_similarity(inv_ref, cand_ref)
            if fuzzy_ref_score >= 90.0:
                ref_score = 15.0
                used_fuzzy = True
                matched_fields.append("reference")
            else:
                mismatched_fields.append("reference")
    else:
        mismatched_fields.append("reference")

    # 4. Date Proximity Match (15 pts max)
    inv_date = invoice_norm.get("date")
    cand_date = candidate_norm.get("date")
    date_diff = calculate_date_difference(inv_date, cand_date)
    date_score = 0.0

    if date_diff <= date_tolerance_days:
        matched_fields.append("date")
        if date_diff == 0:
            date_score = 15.0
        elif date_diff == 1:
            date_score = 13.0
        elif date_diff == 2:
            date_score = 10.0
        elif date_diff == 3:
            date_score = 7.0
        else:
            date_score = max(3.0, round(15.0 - (date_diff / max(1, date_tolerance_days)) * 10.0, 1))
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

    # Determine Matching Method
    if total_score < 40.0:
        matching_method = "NO_MATCH"
    elif not used_fuzzy and total_score == 100.0:
        matching_method = "EXACT"
    elif not used_fuzzy:
        matching_method = "NORMALIZED"
    else:
        matching_method = "FUZZY"

    return {
        "total_score": round(total_score, 2),
        "amount_score": amount_score,
        "customer_name_score": customer_score,
        "fuzzy_customer_score": fuzzy_customer_score,
        "description_similarity": desc_similarity,
        "reference_score": ref_score,
        "date_score": date_score,
        "currency_score": currency_score,
        "matched_fields": matched_fields,
        "mismatched_fields": mismatched_fields,
        "matching_method": matching_method
    }
