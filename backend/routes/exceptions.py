from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from schemas import ExceptionRecord, ExceptionSummaryResponse
from services.exceptions import (
    get_all_exceptions,
    get_exception_by_id,
    get_exceptions_summary
)
from services.reconciliation import (
    get_latest_results,
    load_csv_records,
    run_reconciliation_batch
)
import os

router = APIRouter(prefix="/api/exceptions", tags=["exceptions"])


def ensure_reconciliation_executed():
    """Triggers batch reconciliation run if exception cache is empty."""
    if not get_all_exceptions():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        data_dir = os.path.join(project_root, "data")

        invoices_csv = os.path.join(data_dir, "invoices.csv")
        bank_csv = os.path.join(data_dir, "bank_transactions.csv")
        gateway_csv = os.path.join(data_dir, "gateway_transactions.csv")

        if os.path.exists(invoices_csv):
            invoices = load_csv_records(invoices_csv)
            bank_txns = load_csv_records(bank_csv)
            gateway_txns = load_csv_records(gateway_csv)
            run_reconciliation_batch(invoices, bank_txns, gateway_txns)


@router.get("", response_model=List[ExceptionRecord])
def list_exceptions(
    status: Optional[str] = Query(None, description="Filter by status (OPEN, UNDER_REVIEW, RESOLVED)"),
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    exception_type: Optional[str] = Query(None, description="Filter by exception_type")
):
    """
    Returns list of all active discrepancy exceptions, with optional query parameter filtering.
    """
    ensure_reconciliation_executed()
    return get_all_exceptions(status=status, severity=severity, exception_type=exception_type)


@router.get("/summary", response_model=ExceptionSummaryResponse)
def get_summary_metrics():
    """Returns aggregated summary metrics across all detected exceptions."""
    ensure_reconciliation_executed()
    return get_exceptions_summary()


@router.get("/{exception_id}", response_model=ExceptionRecord)
def get_single_exception(exception_id: str):
    """Returns full details for a specific exception record by ID."""
    ensure_reconciliation_executed()
    exc = get_exception_by_id(exception_id)
    if not exc:
        raise HTTPException(status_code=404, detail=f"Exception record '{exception_id}' not found.")
    return exc
