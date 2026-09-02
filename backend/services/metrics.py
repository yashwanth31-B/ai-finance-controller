"""
Metrics & Ground Truth Evaluation Service
==========================================
Computes batch reconciliation metrics, ground truth verification accuracy,
processing throughput, and scenario breakdown performance.
"""

import os
import csv
from typing import Dict, Any, List
from services.reconciliation import (
    get_latest_results,
    LATEST_RECONCILIATION_BATCH,
    load_csv_records,
    run_reconciliation_batch
)
from services.exceptions import get_all_exceptions


def get_data_dir() -> str:
    """Resolve path to data directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    return os.path.join(project_root, "data")


def load_ground_truth() -> Dict[str, Dict[str, str]]:
    """Loads ground truth CSV mapping invoice_id to expected results."""
    gt_file = os.path.join(get_data_dir(), "ground_truth.csv")
    gt_map: Dict[str, Dict[str, str]] = {}
    if not os.path.exists(gt_file):
        return gt_map

    with open(gt_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inv_id = row.get("invoice_id", "").strip()
            if inv_id:
                gt_map[inv_id] = {
                    "expected_bank_transaction_id": row.get("expected_bank_transaction_id", "").strip(),
                    "expected_gateway_payment_id": row.get("expected_gateway_payment_id", "").strip(),
                    "expected_status": row.get("expected_status", "").strip(),
                    "scenario_type": row.get("scenario_type", "").strip()
                }
    return gt_map


def compute_metrics() -> Dict[str, Any]:
    """
    Computes system-wide operational metrics based on the latest batch execution and ground truth.
    Triggers execution if cache is empty.
    """
    results = get_latest_results()

    # Trigger automatic batch run if results are missing
    if not results:
        data_dir = get_data_dir()
        inv_csv = os.path.join(data_dir, "invoices.csv")
        bank_csv = os.path.join(data_dir, "bank_transactions.csv")
        gw_csv = os.path.join(data_dir, "gateway_transactions.csv")

        if os.path.exists(inv_csv):
            invoices = load_csv_records(inv_csv)
            bank_txns = load_csv_records(bank_csv)
            gw_txns = load_csv_records(gw_csv)
            _, results = run_reconciliation_batch(invoices, bank_txns, gw_txns)

    total_records = len(results)
    if total_records == 0:
        return {
            "total_records": 0,
            "automatically_matched": 0,
            "needs_review": 0,
            "exceptions": 0,
            "match_rate": 0.0,
            "verified_accuracy": 0.0,
            "throughput": 0.0,
            "average_confidence": 0.0,
            "reconciliation_status": {"MATCHED": 0, "REVIEW": 0, "EXCEPTION": 0},
            "exception_breakdown": {},
            "scenario_performance": []
        }

    # Count status metrics
    matched_count = sum(1 for r in results if r.get("status") == "MATCHED")
    review_count = sum(1 for r in results if r.get("status") == "REVIEW")
    exception_count = sum(1 for r in results if r.get("status") == "EXCEPTION")

    match_rate = round((matched_count / total_records) * 100.0, 2)

    # Average confidence score
    avg_confidence = round(
        sum(r.get("overall_confidence_score", 0.0) for r in results) / total_records, 2
    )

    # Throughput
    proc_time = LATEST_RECONCILIATION_BATCH.get("processing_time_seconds", 0.05) if LATEST_RECONCILIATION_BATCH else 0.05
    if proc_time <= 0:
        proc_time = 0.01
    throughput = round(total_records / proc_time, 2)

    # Exception type breakdown
    active_exceptions = get_all_exceptions()
    exception_breakdown: Dict[str, int] = {}
    for exc in active_exceptions:
        exc_type = exc.get("exception_type")
        if exc_type:
            exception_breakdown[exc_type] = exception_breakdown.get(exc_type, 0) + 1

    # Ground truth evaluation & scenario performance
    gt_map = load_ground_truth()
    total_correct = 0
    scenario_stats: Dict[str, Dict[str, int]] = {}

    for r in results:
        inv_id = r.get("invoice_id")
        gt = gt_map.get(inv_id)
        if not gt:
            continue

        scen = gt.get("scenario_type") or "default_scenario"
        if scen not in scenario_stats:
            scenario_stats[scen] = {"total": 0, "correct": 0}

        scenario_stats[scen]["total"] += 1

        exp_bank = gt.get("expected_bank_transaction_id", "")
        exp_gw = gt.get("expected_gateway_payment_id", "")
        exp_status = gt.get("expected_status", "")

        act_bank = r.get("selected_bank_transaction_id") or ""
        act_gw = r.get("selected_gateway_payment_id") or ""
        act_status = r.get("status") or ""

        # Match check against ground truth
        bank_correct = (exp_bank == "" and act_bank == "") or (exp_bank != "" and exp_bank == act_bank)
        gw_correct = (exp_gw == "" and act_gw == "") or (exp_gw != "" and exp_gw == act_gw)
        status_correct = (exp_status == act_status) or (exp_status in ("REVIEW", "EXCEPTION") and act_status in ("REVIEW", "EXCEPTION"))

        if bank_correct and gw_correct and status_correct:
            total_correct += 1
            scenario_stats[scen]["correct"] += 1

    evaluable_total = len(gt_map) if gt_map else total_records
    verified_accuracy = round((total_correct / evaluable_total) * 100.0, 2) if evaluable_total > 0 else match_rate

    scenario_performance = []
    for scen_name, stats in scenario_stats.items():
        tot = stats["total"]
        corr = stats["correct"]
        acc = round((corr / tot) * 100.0, 2) if tot > 0 else 0.0
        # Format scenario label cleanly
        formatted_name = scen_name.replace("_", " ").title()
        scenario_performance.append({
            "scenario_name": formatted_name,
            "total_records": tot,
            "correct_results": corr,
            "accuracy": acc
        })

    # Sort scenarios alphabetically
    scenario_performance.sort(key=lambda x: x["scenario_name"])

    return {
        "total_records": total_records,
        "automatically_matched": matched_count,
        "needs_review": review_count,
        "exceptions": exception_count,
        "match_rate": match_rate,
        "verified_accuracy": verified_accuracy,
        "throughput": throughput,
        "average_confidence": avg_confidence,
        "reconciliation_status": {
            "MATCHED": matched_count,
            "REVIEW": review_count,
            "EXCEPTION": exception_count
        },
        "exception_breakdown": exception_breakdown,
        "scenario_performance": scenario_performance
    }
