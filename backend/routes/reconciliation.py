import os
from typing import List
from fastapi import APIRouter, HTTPException
from schemas import ReconciliationRunResponse, ReconciliationResultItem
from services.reconciliation import (
    load_csv_records,
    run_reconciliation_batch,
    get_latest_results,
    get_result_by_invoice_id
)

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])


def get_data_dir() -> str:
    """Resolve absolute path to data directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    return os.path.join(project_root, "data")


@router.post("/run", response_model=ReconciliationRunResponse)
def execute_reconciliation_run():
    """
    Executes batch 3-way reconciliation on synthetic CSV datasets.
    Loads invoices, bank transactions, and gateway payments, normalizes records in memory,
    runs deterministic matching, stores results, and returns operational batch metrics.
    """
    data_dir = get_data_dir()
    invoices_csv = os.path.join(data_dir, "invoices.csv")
    bank_csv = os.path.join(data_dir, "bank_transactions.csv")
    gateway_csv = os.path.join(data_dir, "gateway_transactions.csv")

    if not os.path.exists(invoices_csv):
        raise HTTPException(status_code=400, detail="Data files missing. Please generate synthetic datasets first.")

    invoices = load_csv_records(invoices_csv)
    bank_txns = load_csv_records(bank_csv)
    gateway_txns = load_csv_records(gateway_csv)

    summary, _ = run_reconciliation_batch(invoices, bank_txns, gateway_txns)
    return summary


@router.get("/results", response_model=List[ReconciliationResultItem])
def get_all_reconciliation_results():
    """Returns all invoice reconciliation results from the latest execution run."""
    results = get_latest_results()
    if not results:
        # If no cached run exists yet, automatically execute a run on current datasets
        data_dir = get_data_dir()
        invoices_csv = os.path.join(data_dir, "invoices.csv")
        bank_csv = os.path.join(data_dir, "bank_transactions.csv")
        gateway_csv = os.path.join(data_dir, "gateway_transactions.csv")
        if os.path.exists(invoices_csv):
            invoices = load_csv_records(invoices_csv)
            bank_txns = load_csv_records(bank_csv)
            gateway_txns = load_csv_records(gateway_csv)
            _, results = run_reconciliation_batch(invoices, bank_txns, gateway_txns)
    return results


@router.get("/results/{invoice_id}", response_model=ReconciliationResultItem)
def get_single_reconciliation_result(invoice_id: str):
    """Returns detailed reconciliation result for a specific invoice."""
    result = get_result_by_invoice_id(invoice_id)
    if not result:
        # Trigger automatic run if cache is empty
        results = get_all_reconciliation_results()
        result = get_result_by_invoice_id(invoice_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"Reconciliation result for invoice '{invoice_id}' not found.")

    return result
