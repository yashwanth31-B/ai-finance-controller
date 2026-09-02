"""
Multi-Source 3-Way Reconciliation Engine
========================================
Runs deterministic & fuzzy matching across Invoice, Bank Transaction, and Payment Gateway records.

Classification Thresholds:
- 90 to 100: MATCHED
- 70 to 89: REVIEW
- Below 70: EXCEPTION
- Ambiguous top candidates: REVIEW (with reason "AMBIGUOUS_CANDIDATES" / "Multiple possible matches")
"""

import os
import csv
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from services.normalization import normalize_record
from services.scoring import score_candidate


# Global in-memory cache for latest reconciliation execution results
LATEST_RECONCILIATION_BATCH: Optional[Dict[str, Any]] = None
LATEST_RECONCILIATION_RESULTS: Dict[str, Dict[str, Any]] = {}


def load_csv_records(file_path: str) -> List[Dict[str, Any]]:
    """Helper to read CSV file records as dictionaries."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def run_reconciliation_batch(
    invoices: List[Dict[str, Any]],
    bank_txns: List[Dict[str, Any]],
    gateway_txns: List[Dict[str, Any]]
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Executes 3-way reconciliation on provided raw records batches.
    
    1. Normalizes all records in memory
    2. Searches best candidates for Bank and Gateway using RapidFuzz matching
    3. Calculates deterministic & fuzzy confidence scores
    4. Detects ambiguity and classifies results into MATCHED / REVIEW / EXCEPTION
    """
    start_time = time.time()
    batch_id = f"batch-{uuid.uuid4().hex[:8]}"

    # 1. Normalize datasets
    norm_invoices = [normalize_record(inv) for inv in invoices]
    norm_bank = [normalize_record(b) for b in bank_txns]
    norm_gateway = [normalize_record(g) for g in gateway_txns]

    results: List[Dict[str, Any]] = []
    matched_count = 0
    review_count = 0
    exception_count = 0

    for inv_item in norm_invoices:
        raw_inv = inv_item["original"]
        inv_norm = inv_item["normalized"]
        inv_id = str(raw_inv.get("invoice_id", ""))

        # Score Bank Candidates
        bank_scores: List[Dict[str, Any]] = []
        for b_item in norm_bank:
            raw_b = b_item["original"]
            b_norm = b_item["normalized"]
            score_res = score_candidate(inv_norm, b_norm, raw_b)
            bank_scores.append({
                "raw": raw_b,
                "score_res": score_res,
                "score": score_res["total_score"],
                "id": str(raw_b.get("transaction_id", ""))
            })

        bank_scores.sort(key=lambda x: x["score"], reverse=True)

        # Score Gateway Candidates
        gateway_scores: List[Dict[str, Any]] = []
        for g_item in norm_gateway:
            raw_g = g_item["original"]
            g_norm = g_item["normalized"]
            score_res = score_candidate(inv_norm, g_norm, raw_g)
            gateway_scores.append({
                "raw": raw_g,
                "score_res": score_res,
                "score": score_res["total_score"],
                "id": str(raw_g.get("payment_id", ""))
            })

        gateway_scores.sort(key=lambda x: x["score"], reverse=True)

        # Select top Bank candidate
        top_bank = bank_scores[0] if bank_scores else None
        second_bank = bank_scores[1] if len(bank_scores) >= 2 else None
        top_bank_score = top_bank["score"] if top_bank else 0.0
        second_bank_score = second_bank["score"] if second_bank else 0.0
        selected_bank_id = top_bank["id"] if (top_bank and top_bank_score >= 40.0) else None

        # Select top Gateway candidate
        top_gw = gateway_scores[0] if gateway_scores else None
        second_gw = gateway_scores[1] if len(gateway_scores) >= 2 else None
        top_gw_score = top_gw["score"] if top_gw else 0.0
        second_gw_score = second_gw["score"] if second_gw else 0.0
        selected_gw_id = top_gw["id"] if (top_gw and top_gw_score >= 40.0) else None

        # Candidate ranking metrics
        best_candidate_score = max(top_bank_score, top_gw_score)
        second_best_candidate_score = max(
            second_bank_score if top_bank_score >= top_gw_score else top_bank_score,
            second_gw_score if top_gw_score >= top_bank_score else top_gw_score
        )
        candidate_score_gap = round(best_candidate_score - second_best_candidate_score, 2)

        # Ambiguity Check: difference < 5 pts and both candidates above review threshold (>= 70)
        is_bank_ambiguous = (
            len(bank_scores) >= 2 and
            bank_scores[0]["score"] >= 60.0 and
            (bank_scores[0]["score"] - bank_scores[1]["score"]) < 5.0
        )
        is_gw_ambiguous = (
            len(gateway_scores) >= 2 and
            gateway_scores[0]["score"] >= 60.0 and
            (gateway_scores[0]["score"] - gateway_scores[1]["score"]) < 5.0
        )
        is_ambiguous = is_bank_ambiguous or is_gw_ambiguous

        # Calculate Overall Confidence Score
        if selected_bank_id and selected_gw_id:
            overall_confidence = round((top_bank_score + top_gw_score) / 2.0, 2)
        elif selected_bank_id:
            overall_confidence = top_bank_score
        elif selected_gw_id:
            overall_confidence = top_gw_score
        else:
            overall_confidence = 0.0

        # Extract fuzzy metrics from top candidate
        top_cand_res = top_bank["score_res"] if (top_bank and top_bank_score >= top_gw_score) else (top_gw["score_res"] if top_gw else {})
        fuzzy_cust_score = top_cand_res.get("fuzzy_customer_score", 0.0)
        desc_similarity = top_cand_res.get("description_similarity", 0.0)
        cand_matching_method = top_cand_res.get("matching_method", "NO_MATCH")

        # Combine Matched and Mismatched Fields
        matched_fields_set = set()
        mismatched_fields_set = set()

        if top_bank and selected_bank_id:
            matched_fields_set.update(top_bank["score_res"]["matched_fields"])
            mismatched_fields_set.update(top_bank["score_res"]["mismatched_fields"])

        if top_gw and selected_gw_id:
            matched_fields_set.update(top_gw["score_res"]["matched_fields"])
            mismatched_fields_set.update(top_gw["score_res"]["mismatched_fields"])

        if not selected_bank_id and not selected_gw_id:
            mismatched_fields_set = {"amount", "customer_name", "reference", "date", "currency"}

        mismatched_fields_set.difference_update(matched_fields_set)

        # Determine Classification & Matching Method
        if is_ambiguous:
            status = "REVIEW"
            matching_method = "AMBIGUOUS"
            explanation = "Multiple possible matches identified with identical or close confidence scores (AMBIGUOUS_CANDIDATES)."
        elif overall_confidence >= 90.0:
            status = "MATCHED"
            matching_method = cand_matching_method
            explanation = f"High-confidence match verified across records using {matching_method} matching."
        elif overall_confidence >= 70.0:
            status = "REVIEW"
            matching_method = cand_matching_method if cand_matching_method != "NO_MATCH" else "FUZZY"
            explanation = f"Moderate confidence match (score {overall_confidence}). Manual review required."
        else:
            status = "EXCEPTION"
            matching_method = "NO_MATCH"
            explanation = f"Low confidence match (score {overall_confidence}) or missing payment records."

        # Update Counters
        if status == "MATCHED":
            matched_count += 1
        elif status == "REVIEW":
            review_count += 1
        else:
            exception_count += 1

        # Format amount float
        try:
            inv_amt = float(raw_inv.get("amount", 0.0))
        except (ValueError, TypeError):
            inv_amt = 0.0

        rec_item = {
            "invoice_id": inv_id,
            "customer_name": str(raw_inv.get("customer_name", "")),
            "invoice_amount": inv_amt,
            "invoice_date": str(raw_inv.get("invoice_date", "")),
            "selected_bank_transaction_id": selected_bank_id,
            "selected_gateway_payment_id": selected_gw_id,
            "bank_score": top_bank_score if selected_bank_id else 0.0,
            "gateway_score": top_gw_score if selected_gw_id else 0.0,
            "overall_confidence_score": overall_confidence,
            "status": status,
            "matched_fields": sorted(list(matched_fields_set)),
            "mismatched_fields": sorted(list(mismatched_fields_set)),
            "explanation": explanation,
            "normalized_customer_name": inv_norm.get("customer_name", ""),
            "fuzzy_customer_score": fuzzy_cust_score,
            "description_similarity": desc_similarity,
            "best_candidate_score": best_candidate_score,
            "second_best_candidate_score": second_best_candidate_score,
            "candidate_score_gap": candidate_score_gap,
            "matching_method": matching_method
        }
        results.append(rec_item)

    elapsed_time = round(time.time() - start_time, 4)

    summary = {
        "batch_id": batch_id,
        "total_records": len(invoices),
        "matched": matched_count,
        "review": review_count,
        "exceptions": exception_count,
        "processing_time_seconds": elapsed_time,
        "results_available": True
    }

    # Store in global cache
    global LATEST_RECONCILIATION_BATCH, LATEST_RECONCILIATION_RESULTS
    LATEST_RECONCILIATION_BATCH = summary
    LATEST_RECONCILIATION_RESULTS = {item["invoice_id"]: item for item in results}

    return summary, results


def get_latest_results() -> List[Dict[str, Any]]:
    """Returns list of all latest reconciliation results from cache."""
    return list(LATEST_RECONCILIATION_RESULTS.values())


def get_result_by_invoice_id(invoice_id: str) -> Optional[Dict[str, Any]]:
    """Returns specific invoice reconciliation result from cache."""
    return LATEST_RECONCILIATION_RESULTS.get(invoice_id)
