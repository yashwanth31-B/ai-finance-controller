from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session

from database import get_db
import services.reports as reports_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/reconciliation.csv")
def download_reconciliation_csv():
    """
    Export full reconciliation results as CSV.
    Headers include invoice_id, customer_name, invoice_amount, bank_transaction_id,
    gateway_payment_id, confidence_score, status, exception_type, severity, final_status.
    """
    results = reports_service.ensure_reconciliation_data()
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    csv_content = reports_service.generate_reconciliation_csv()
    if not csv_content:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="reconciliation_report.csv"'
        }
    )


@router.get("/exceptions.csv")
def download_exceptions_csv():
    """
    Export discrepancy exceptions as CSV.
    Headers include invoice_id, exception_type, severity, confidence_score, reason, suggested_action, status.
    """
    results = reports_service.ensure_reconciliation_data()
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    csv_content = reports_service.generate_exceptions_csv()
    if not csv_content:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="exceptions_report.csv"'
        }
    )


@router.get("/audit.csv")
def download_audit_csv(db: Session = Depends(get_db)):
    """
    Export immutable audit trail event log as CSV.
    Headers include timestamp, invoice_id, actor, event_type, previous_state, new_state, note.
    """
    results = reports_service.ensure_reconciliation_data()
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    csv_content = reports_service.generate_audit_csv(db=db)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="audit_trail_report.csv"'
        }
    )


@router.get("/summary.pdf")
def download_summary_pdf(db: Session = Depends(get_db)):
    """
    Export dynamic executive PDF summary report.
    Includes Title, Generation Timestamp, Batch ID, KPI Summary, Exception Breakdown,
    Top Unresolved Exceptions, and Audit Activity Summary.
    """
    results = reports_service.ensure_reconciliation_data()
    if not results:
        raise HTTPException(
            status_code=400,
            detail="No report data available. Run reconciliation first."
        )

    pdf_bytes = reports_service.generate_summary_pdf(db=db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="reconciliation_summary.pdf"'
        }
    )
