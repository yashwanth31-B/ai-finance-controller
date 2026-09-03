"""
AI Finance Q&A Assistant Engine
===============================
Provides deterministic financial Q&A over active reconciliation batch results,
exception records, operational KPIs, and audit trail records.
"""

import re
from typing import Dict, Any, List
from services.reconciliation import get_latest_results, get_result_by_invoice_id, LATEST_RECONCILIATION_BATCH
from services.exceptions import get_all_exceptions
from services.metrics import compute_metrics


def answer_finance_question(question: str) -> Dict[str, Any]:
    """
    Processes natural-language financial query using active system reconciliation data.
    Returns structured answer, related invoice IDs, and data sources used.
    """
    q_clean = (question or "").strip()
    q_lower = q_clean.lower()

    # 1. Specific Invoice Lookup Query (e.g. "Why is INV091 an exception?", "Why was INV113 sent to review?")
    inv_match = re.search(r'\b(INV\d+)\b', q_clean, re.IGNORECASE)
    if inv_match:
        target_inv_id = inv_match.group(1).upper()
        result = get_result_by_invoice_id(target_inv_id)

        if result:
            status = result.get("status", "UNKNOWN")
            exc_type = result.get("exception_type") or "None"
            confidence = result.get("overall_confidence_score", 0.0)
            explanation = result.get("explanation", "")
            action = result.get("suggested_action") or "No action required"
            inv_amt = result.get("invoice_amount", 0.0)
            bank_id = result.get("selected_bank_transaction_id") or "Missing"
            gw_id = result.get("selected_gateway_payment_id") or "Missing"

            if status == "EXCEPTION":
                ans = (
                    f"Invoice {target_inv_id} (₹{inv_amt:.2f}) is an EXCEPTION due to {exc_type.replace('_', ' ')}. "
                    f"Confidence score: {confidence}%. {explanation} "
                    f"Selected Bank ID: {bank_id}, Gateway ID: {gw_id}. "
                    f"Recommended Action: {action}."
                )
            elif status == "REVIEW":
                ans = (
                    f"Invoice {target_inv_id} (₹{inv_amt:.2f}) was sent to REVIEW due to {exc_type.replace('_', ' ')}. "
                    f"Confidence score: {confidence}%. {explanation} "
                    f"Recommended Action: {action}."
                )
            else:
                ans = (
                    f"Invoice {target_inv_id} (₹{inv_amt:.2f}) was successfully MATCHED. "
                    f"Confidence score: {confidence}%. Bank ID: {bank_id}, Gateway ID: {gw_id}."
                )

            return {
                "answer": ans,
                "related_invoice_ids": [target_inv_id],
                "data_sources_used": ["reconciliation_batch_cache", "exceptions_engine"]
            }
        else:
            return {
                "answer": f"Invoice '{target_inv_id}' was not found in the current reconciliation batch execution.",
                "related_invoice_ids": [],
                "data_sources_used": ["reconciliation_batch_cache"]
            }

    # 2. Match Rate & System Performance Metrics
    if any(k in q_lower for k in ["match rate", "accuracy", "processed", "throughput", "batch size"]):
        metrics = compute_metrics()
        total_recs = metrics.get("total_records", 0)
        match_rate = metrics.get("match_rate", 0.0)
        matched = metrics.get("automatically_matched", 0)
        review = metrics.get("needs_review", 0)
        exceptions = metrics.get("exceptions", 0)
        ver_acc = metrics.get("verified_accuracy")
        ver_acc_str = f"{ver_acc:.1f}%" if ver_acc is not None else "N/A (Ground Truth required)"

        ans = (
            f"The latest batch processed {total_recs} records with an automated match rate of {match_rate:.1f}%. "
            f"Results: {matched} MATCHED, {review} REVIEW, {exceptions} EXCEPTION. "
            f"Verified ground truth accuracy is {ver_acc_str}."
        )
        return {
            "answer": ans,
            "related_invoice_ids": [],
            "data_sources_used": ["operational_metrics_service"]
        }

    # 3. Duplicate Payment Queries
    if "duplicate" in q_lower:
        results = get_latest_results()
        dup_results = [r for r in results if r.get("exception_type") == "DUPLICATE_PAYMENT"]
        dup_ids = [r["invoice_id"] for r in dup_results]

        if dup_ids:
            ans = f"Found {len(dup_ids)} duplicate payment exceptions: {', '.join(dup_ids)}. Payment records were reused across multiple invoices."
        else:
            ans = "No duplicate payment exceptions detected in the current reconciliation batch."

        return {
            "answer": ans,
            "related_invoice_ids": dup_ids,
            "data_sources_used": ["reconciliation_results"]
        }

    # 4. Total Exception Summary Query
    if "how many exceptions" in q_lower or "count of exceptions" in q_lower or "total exceptions" in q_lower:
        exceptions_list = get_all_exceptions()
        total_exc = len(exceptions_list)
        if total_exc > 0:
            by_type = {}
            for e in exceptions_list:
                t = e.get("exception_type", "UNKNOWN")
                by_type[t] = by_type.get(t, 0) + 1
            breakdown_str = ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in by_type.items()])
            ans = f"There are currently {total_exc} active reconciliation exceptions. Breakdown: {breakdown_str}."
        else:
            ans = "There are zero active reconciliation exceptions."

        return {
            "answer": ans,
            "related_invoice_ids": [e.get("invoice_id") for e in exceptions_list if e.get("invoice_id")],
            "data_sources_used": ["exceptions_summary_engine"]
        }

    # 5. Lowest Confidence / High Risk Records Query
    if "lowest confidence" in q_lower or "high risk" in q_lower or "risk" in q_lower:
        results = get_latest_results()
        if results:
            sorted_res = sorted(results, key=lambda x: x.get("overall_confidence_score", 0.0))
            lowest = sorted_res[:3]
            lowest_info = [f"{r['invoice_id']} (score: {r['overall_confidence_score']}%, status: {r['status']})" for r in lowest]
            ans = f"The lowest confidence records in the current batch are: {', '.join(lowest_info)}."
            return {
                "answer": ans,
                "related_invoice_ids": [r["invoice_id"] for r in lowest],
                "data_sources_used": ["reconciliation_confidence_scoring"]
            }

    # 6. Unresolved Amount Mismatches Query
    if "amount mismatch" in q_lower or "amount discrepancy" in q_lower:
        exceptions_list = get_all_exceptions()
        amt_mismatches = [e for e in exceptions_list if e.get("exception_type") == "AMOUNT_MISMATCH"]
        amt_ids = [e.get("invoice_id") for e in amt_mismatches]
        if amt_ids:
            ans = f"Found {len(amt_ids)} unresolved amount mismatch exceptions: {', '.join(amt_ids)}."
        else:
            ans = "No unresolved amount mismatch exceptions found in the active batch."
        return {
            "answer": ans,
            "related_invoice_ids": amt_ids,
            "data_sources_used": ["exceptions_engine"]
        }

    # Fallback response when query cannot be answered from current data
    return {
        "answer": "I cannot determine that from the current reconciliation data.",
        "related_invoice_ids": [],
        "data_sources_used": ["reconciliation_batch_cache"]
    }
