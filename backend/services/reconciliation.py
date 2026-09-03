"""
Multi-Source 3-Way Reconciliation Engine & Exception Classifier
================================================================
Runs deterministic & fuzzy matching across Invoice, Bank Transaction, and Payment Gateway records,
classifying exceptions and generating structured audit records based on dynamic system settings.
"""

import os
import csv
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from services.normalization import normalize_record
from services.scoring import score_candidate
from services.settings import get_active_settings
from services.exceptions import (
    reset_exceptions_cache,
    generate_exception_record,
    SEVERITY_LEVELS,
    SUGGESTED_ACTIONS
)
from services.notifications import create_notification



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
    gateway_txns: List[Dict[str, Any]],
    db: Optional[Session] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Executes 3-way reconciliation on provided raw records batches using active system settings.
    
    1. Reads active settings (amount_tolerance, date_tolerance_days, thresholds, candidate_score_gap)
    2. Normalizes all records in memory
    3. Searches best candidates for Bank and Gateway using RapidFuzz matching & active settings
    4. Calculates deterministic & fuzzy confidence scores
    5. Detects transaction reuse / duplicate payment conflicts across batch
    6. Classifies exceptions across discrepancy categories according to configured rules
    """
    start_time = time.time()
    batch_id = f"batch-{uuid.uuid4().hex[:8]}"

    # Fetch active settings
    settings = get_active_settings(db=db)
    amount_tolerance = float(settings.get("amount_tolerance", 0.0))
    date_tolerance_days = int(settings.get("date_tolerance_days", 3))
    auto_match_threshold = float(settings.get("auto_match_threshold", 90.0))
    review_threshold = float(settings.get("review_threshold", 70.0))
    fuzzy_similarity_threshold = float(settings.get("fuzzy_similarity_threshold", 70.0))
    candidate_score_gap_threshold = float(settings.get("candidate_score_gap", 10.0))

    # Reset exceptions cache for fresh run execution
    reset_exceptions_cache()

    # 1. Normalize datasets
    norm_invoices = [normalize_record(inv) for inv in invoices]
    norm_bank = [normalize_record(b) for b in bank_txns]
    norm_gateway = [normalize_record(g) for g in gateway_txns]

    prelim_results: List[Dict[str, Any]] = []
    bank_id_assignments: Dict[str, List[str]] = {}
    gw_id_assignments: Dict[str, List[str]] = {}

    for inv_item in norm_invoices:
        raw_inv = inv_item["original"]
        inv_norm = inv_item["normalized"]
        inv_id = str(raw_inv.get("invoice_id", ""))

        # Score Bank Candidates
        bank_scores: List[Dict[str, Any]] = []
        for b_item in norm_bank:
            raw_b = b_item["original"]
            b_norm = b_item["normalized"]
            score_res = score_candidate(inv_norm, b_norm, raw_b, settings=settings)
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
            score_res = score_candidate(inv_norm, g_norm, raw_g, settings=settings)
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

        # Record assignment frequency for duplicate transaction reuse detection
        if selected_bank_id:
            bank_id_assignments.setdefault(selected_bank_id, []).append(inv_id)
        if selected_gw_id:
            gw_id_assignments.setdefault(selected_gw_id, []).append(inv_id)

        # Candidate ranking metrics
        best_candidate_score = max(top_bank_score, top_gw_score)
        second_best_candidate_score = max(
            second_bank_score if top_bank_score >= top_gw_score else top_bank_score,
            second_gw_score if top_gw_score >= top_bank_score else top_gw_score
        )
        candidate_score_gap = round(best_candidate_score - second_best_candidate_score, 2)

        # Ambiguity Check based on configured candidate_score_gap_threshold
        is_bank_ambiguous = (
            len(bank_scores) >= 2 and
            bank_scores[0]["score"] >= review_threshold and
            (bank_scores[0]["score"] - bank_scores[1]["score"]) < candidate_score_gap_threshold
        )
        is_gw_ambiguous = (
            len(gateway_scores) >= 2 and
            gateway_scores[0]["score"] >= review_threshold and
            (gateway_scores[0]["score"] - gateway_scores[1]["score"]) < candidate_score_gap_threshold
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

        # Format amount float
        try:
            inv_amt = float(raw_inv.get("amount", 0.0))
        except (ValueError, TypeError):
            inv_amt = 0.0

        prelim_results.append({
            "raw_inv": raw_inv,
            "inv_norm": inv_norm,
            "invoice_id": inv_id,
            "customer_name": str(raw_inv.get("customer_name", "")),
            "invoice_amount": inv_amt,
            "invoice_date": str(raw_inv.get("invoice_date", "")),
            "invoice_currency": str(raw_inv.get("currency", "")),
            "selected_bank_id": selected_bank_id,
            "selected_gw_id": selected_gw_id,
            "top_bank": top_bank,
            "top_gw": top_gw,
            "top_bank_score": top_bank_score,
            "top_gw_score": top_gw_score,
            "overall_confidence": overall_confidence,
            "is_ambiguous": is_ambiguous,
            "matched_fields_set": matched_fields_set,
            "mismatched_fields_set": mismatched_fields_set,
            "fuzzy_cust_score": fuzzy_cust_score,
            "desc_similarity": desc_similarity,
            "best_candidate_score": best_candidate_score,
            "second_best_candidate_score": second_best_candidate_score,
            "candidate_score_gap": candidate_score_gap,
            "cand_matching_method": cand_matching_method,
            "bank_scores": bank_scores,
            "gateway_scores": gateway_scores
        })

    # Second Pass: Duplicate transaction check, final classification, and exception generation
    results: List[Dict[str, Any]] = []
    matched_count = 0
    review_count = 0
    exception_count = 0

    for p in prelim_results:
        inv_id = p["invoice_id"]
        inv_amt = p["invoice_amount"]
        selected_bank_id = p["selected_bank_id"]
        selected_gw_id = p["selected_gw_id"]
        overall_confidence = p["overall_confidence"]
        is_ambiguous = p["is_ambiguous"]
        cand_matching_method = p["cand_matching_method"]

        # Duplicate payment check across batch
        is_duplicate = (
            (selected_bank_id and len(bank_id_assignments.get(selected_bank_id, [])) > 1) or
            (selected_gw_id and len(gw_id_assignments.get(selected_gw_id, [])) > 1)
        )

        # Gateway Fee Detection
        top_g = p["top_gw"]
        gw_cand = top_g["raw"] if top_g else {}
        gw_amt = 0.0
        gw_fee = 0.0
        gw_net = 0.0
        gw_gross = 0.0
        is_gateway_fee_case = False
        if top_g:
            try:
                gw_amt = float(gw_cand.get("amount", 0.0))
                gw_fee = float(gw_cand.get("fee", 0.0))
                gw_net = float(gw_cand.get("net_amount", 0.0))
                if gw_net == 0.0 and gw_amt > gw_fee:
                    gw_net = gw_amt - gw_fee
                gw_gross = gw_amt if (gw_amt > gw_net) else (gw_net + gw_fee)
                if gw_fee > 0 and gw_net > 0 and abs(gw_fee - (inv_amt - gw_net)) < 0.01:
                    is_gateway_fee_case = True
            except (ValueError, TypeError):
                pass

        # Initial Status Determination using active configured thresholds
        if is_duplicate:
            status = "EXCEPTION"
            matching_method = "NO_MATCH"
            explanation = "Transaction ID assigned to multiple invoices in batch (DUPLICATE_PAYMENT)."
        elif is_ambiguous:
            status = "REVIEW"
            matching_method = "AMBIGUOUS"
            explanation = f"Multiple possible matches identified within candidate score gap ({candidate_score_gap_threshold} pts)."
        elif overall_confidence >= auto_match_threshold:
            status = "MATCHED"
            matching_method = cand_matching_method
            explanation = f"High-confidence match (score {overall_confidence} >= {auto_match_threshold}) verified across records using {matching_method} matching."
        elif is_gateway_fee_case:
            status = "REVIEW"
            matching_method = cand_matching_method if cand_matching_method != "NO_MATCH" else "NORMALIZED"
            explanation = f"Gateway net settlement (₹{gw_net}) differs from gross invoice (₹{inv_amt}) due to ₹{gw_fee} gateway fee."
        elif overall_confidence >= review_threshold:
            status = "REVIEW"
            matching_method = cand_matching_method if cand_matching_method != "NO_MATCH" else "FUZZY"
            explanation = f"Moderate confidence match (score {overall_confidence} >= {review_threshold}). Manual review required."
        else:
            status = "EXCEPTION"
            matching_method = "NO_MATCH"
            explanation = f"Low confidence match (score {overall_confidence} < {review_threshold}) or missing payment records."

        # Exception Classification & Record Generation
        exc_id = None
        exc_type = None
        severity = None
        suggested_action = None

        has_missing_feed = (selected_bank_id is None) or (selected_gw_id is None)

        bank_cand_amt = 0.0
        if selected_bank_id:
            top_b_raw = p["top_bank"]["raw"] if p["top_bank"] else {}
            try:
                bank_cand_amt = float(top_b_raw.get("amount", 0.0))
            except (ValueError, TypeError):
                pass
        bank_matches_perfectly = selected_bank_id and abs(inv_amt - bank_cand_amt) <= (amount_tolerance + 1e-6)
        reportable_gateway_fee = is_gateway_fee_case and bank_matches_perfectly

        if status != "MATCHED" or is_duplicate or has_missing_feed or reportable_gateway_fee:
            top_b = p["top_bank"]
            bank_cand = top_b["raw"] if top_b else {}

            cand_amt = 0.0
            cand_curr = ""
            if top_b and selected_bank_id:
                try:
                    cand_amt = float(bank_cand.get("amount", 0.0))
                except (ValueError, TypeError):
                    pass
                cand_curr = str(bank_cand.get("currency", ""))
            elif top_g and selected_gw_id:
                try:
                    cand_amt = float(gw_cand.get("amount", 0.0))
                except (ValueError, TypeError):
                    pass
                cand_curr = str(gw_cand.get("currency", ""))

            # Classify in priority order using configured tolerances
            if is_duplicate:
                exc_type = "DUPLICATE_PAYMENT"
                reason = f"Payment record (Bank: {selected_bank_id}, Gateway: {selected_gw_id}) is reused across multiple invoices."
            elif cand_curr and p["invoice_currency"] and cand_curr.upper() != p["invoice_currency"].upper():
                exc_type = "CURRENCY_MISMATCH"
                reason = f"Currency mismatch: Invoice ({p['invoice_currency']}) vs Payment ({cand_curr})."
            elif is_ambiguous:
                exc_type = "AMBIGUOUS_MATCH"
                reason = f"Multiple candidate payments yielded scores within candidate score gap ({candidate_score_gap_threshold} pts)."
            elif selected_bank_id is None and selected_gw_id is None:
                exc_type = "MISSING_BANK_PAYMENT"
                reason = "No viable bank or gateway payment candidate was found for this invoice."
            elif selected_bank_id is None:
                exc_type = "MISSING_BANK_PAYMENT"
                reason = "No matching bank statement transaction found for invoice."
            elif cand_amt > 0 and abs(inv_amt - cand_amt) > (amount_tolerance + 1e-6) and not reportable_gateway_fee:
                exc_type = "AMOUNT_MISMATCH"
                reason = f"Amount discrepancy: Invoice (₹{inv_amt}) vs Payment (₹{cand_amt}) exceeds tolerance (₹{amount_tolerance})."
            elif selected_gw_id is None:
                exc_type = "MISSING_GATEWAY_PAYMENT"
                reason = "No matching payment gateway settlement found for invoice."
            elif reportable_gateway_fee:
                exc_type = "POSSIBLE_GATEWAY_FEE"
                reason = f"Gateway net settlement (₹{gw_net}) differs from invoice (₹{inv_amt}) due to ₹{gw_fee} gateway fee."
            elif cand_amt > 0 and abs(inv_amt - cand_amt) > (amount_tolerance + 1e-6):
                exc_type = "AMOUNT_MISMATCH"
                reason = f"Amount discrepancy: Invoice (₹{inv_amt}) vs Payment (₹{cand_amt}) exceeds tolerance (₹{amount_tolerance})."
            elif "customer_name" in p["mismatched_fields_set"] and (top_b or top_g):
                exc_type = "CUSTOMER_MISMATCH"
                reason = f"Weak customer name alignment (below {fuzzy_similarity_threshold}% fuzzy threshold): '{p['customer_name']}'."
            elif "reference" in p["mismatched_fields_set"] and (top_b or top_g):
                exc_type = "REFERENCE_MISMATCH"
                reason = f"Reference mismatch for invoice '{inv_id}'."
            elif "date" in p["mismatched_fields_set"] and (top_b or top_g):
                exc_type = "DATE_OUT_OF_RANGE"
                reason = f"Payment date is outside allowed proximity tolerance ({date_tolerance_days} days) for invoice '{inv_id}'."
            else:
                exc_type = "AMOUNT_MISMATCH"
                reason = f"Reconciliation discrepancy for invoice '{inv_id}'."

            # Calculate metrics for exception record
            amt_diff = abs(inv_amt - cand_amt) if (cand_amt > 0 and exc_type == "AMOUNT_MISMATCH") else None
            pct_diff = ((amt_diff / inv_amt) * 100.0) if (amt_diff and inv_amt > 0) else None

            bank_candidate_ids = [b["id"] for b in p["bank_scores"][:2]] if p["bank_scores"] else []
            gw_candidate_ids = [g["id"] for g in p["gateway_scores"][:2]] if p["gateway_scores"] else []

            exc_record = generate_exception_record(
                batch_id=batch_id,
                invoice_id=inv_id,
                exception_type=exc_type,
                confidence_score=overall_confidence,
                reason=reason,
                bank_ids=bank_candidate_ids,
                gateway_ids=gw_candidate_ids,
                amount_diff=amt_diff,
                pct_diff=pct_diff,
                gross_amount=gw_gross if is_gateway_fee_case else None,
                fee=gw_fee if is_gateway_fee_case else None,
                net_amount=gw_net if is_gateway_fee_case else None
            )

            exc_id = exc_record["exception_id"]
            severity = exc_record["severity"]
            suggested_action = exc_record["suggested_action"]

        # Update Counters
        if status == "MATCHED":
            matched_count += 1
        elif status == "REVIEW":
            review_count += 1
        else:
            exception_count += 1

        rec_item = {
            "invoice_id": inv_id,
            "customer_name": p["customer_name"],
            "invoice_amount": inv_amt,
            "invoice_date": p["invoice_date"],
            "selected_bank_transaction_id": selected_bank_id,
            "selected_gateway_payment_id": selected_gw_id,
            "bank_score": p["top_bank_score"] if selected_bank_id else 0.0,
            "gateway_score": p["top_gw_score"] if selected_gw_id else 0.0,
            "overall_confidence_score": overall_confidence,
            "status": status,
            "matched_fields": sorted(list(p["matched_fields_set"])),
            "mismatched_fields": sorted(list(p["mismatched_fields_set"])),
            "explanation": explanation,
            "normalized_customer_name": p["inv_norm"].get("customer_name", ""),
            "fuzzy_customer_score": p["fuzzy_cust_score"],
            "description_similarity": p["desc_similarity"],
            "best_candidate_score": p["best_candidate_score"],
            "second_best_candidate_score": p["second_best_candidate_score"],
            "candidate_score_gap": p["candidate_score_gap"],
            "matching_method": matching_method,
            "exception_id": exc_id,
            "exception_type": exc_type,
            "severity": severity,
            "suggested_action": suggested_action
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

    # Emit real system notifications for completed batch
    try:
        create_notification(
            type="SUCCESS",
            title="Reconciliation Batch Completed",
            message=f"Reconciliation batch {batch_id} completed successfully ({matched_count} matched, {review_count} review, {exception_count} exceptions).",
            batch_id=batch_id,
            db=db
        )
        if exception_count > 0:
            create_notification(
                type="CRITICAL",
                title="Exceptions Detected",
                message=f"{exception_count} reconciliation exceptions detected in batch {batch_id}.",
                batch_id=batch_id,
                db=db
            )

        review_records = [r for r in results if r.get("status") == "REVIEW"]
        if review_records:
            top_rev = review_records[0]
            create_notification(
                type="WARNING",
                title="Manual Review Required",
                message=f"{top_rev['invoice_id']} requires manual review.",
                invoice_id=top_rev['invoice_id'],
                batch_id=batch_id,
                db=db
            )
    except Exception:
        pass

    return summary, results


def get_latest_results() -> List[Dict[str, Any]]:
    """Returns list of all latest reconciliation results from cache."""
    return list(LATEST_RECONCILIATION_RESULTS.values())


def get_result_by_invoice_id(invoice_id: str) -> Optional[Dict[str, Any]]:
    """Returns specific invoice reconciliation result from cache."""
    return LATEST_RECONCILIATION_RESULTS.get(invoice_id)
