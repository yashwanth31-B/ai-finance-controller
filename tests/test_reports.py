import os
import sys
import io
import csv
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
import services.reconciliation as recon_service

client = TestClient(app)


def test_reconciliation_csv_export():
    """Verify GET /api/reports/reconciliation.csv returns valid CSV file with correct headers and content type."""
    response = client.get("/api/reports/reconciliation.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert 'attachment; filename="reconciliation_report.csv"' in response.headers.get("content-disposition", "")

    content = response.text
    assert "invoice_id,customer_name,invoice_amount" in content
    assert "bank_transaction_id,gateway_payment_id,confidence_score,status,exception_type,severity,final_status" in content

    # Parse CSV structure
    reader = list(csv.DictReader(io.StringIO(content)))
    assert len(reader) > 0
    first_row = reader[0]
    assert "invoice_id" in first_row
    assert "customer_name" in first_row
    assert "invoice_amount" in first_row
    assert "bank_transaction_id" in first_row
    assert "gateway_payment_id" in first_row
    assert "confidence_score" in first_row
    assert "status" in first_row
    assert "final_status" in first_row


def test_exceptions_csv_export():
    """Verify GET /api/reports/exceptions.csv returns valid exception export."""
    response = client.get("/api/reports/exceptions.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert 'attachment; filename="exceptions_report.csv"' in response.headers.get("content-disposition", "")

    content = response.text
    assert "invoice_id,exception_type,severity,confidence_score,reason,suggested_action,status" in content
    reader = list(csv.DictReader(io.StringIO(content)))
    assert len(reader) > 0
    first_row = reader[0]
    assert "invoice_id" in first_row
    assert "exception_type" in first_row
    assert "severity" in first_row
    assert "reason" in first_row


def test_audit_csv_export():
    """Verify GET /api/reports/audit.csv returns valid audit trail export."""
    response = client.get("/api/reports/audit.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    assert 'attachment; filename="audit_trail_report.csv"' in response.headers.get("content-disposition", "")

    content = response.text
    assert "timestamp,invoice_id,actor,event_type,previous_state,new_state,note" in content


def test_summary_pdf_export():
    """Verify GET /api/reports/summary.pdf returns valid PDF file."""
    response = client.get("/api/reports/summary.pdf")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert 'attachment; filename="reconciliation_summary.pdf"' in response.headers.get("content-disposition", "")

    # PDF content magic bytes check (%PDF-)
    content_bytes = response.content
    assert len(content_bytes) > 0
    assert content_bytes.startswith(b"%PDF-")


def test_reports_use_actual_reconciliation_data():
    """Verify that reports export matches actual reconciliation result records from latest run."""
    # Fetch direct reconciliation results
    results_resp = client.get("/api/reconciliation/results")
    assert results_resp.status_code == 200
    actual_results = results_resp.json()
    actual_invoice_ids = {r["invoice_id"] for r in actual_results}

    # Fetch CSV export
    csv_resp = client.get("/api/reports/reconciliation.csv")
    assert csv_resp.status_code == 200
    reader = list(csv.DictReader(io.StringIO(csv_resp.text)))
    exported_invoice_ids = {row["invoice_id"] for row in reader}

    assert actual_invoice_ids == exported_invoice_ids


def test_no_data_case():
    """Verify 400 response with exact error message when no reconciliation data exists."""
    with patch("services.reports.ensure_reconciliation_data", return_value=[]):
        resp_csv = client.get("/api/reports/reconciliation.csv")
        assert resp_csv.status_code == 400
        assert resp_csv.json()["detail"] == "No report data available. Run reconciliation first."

        resp_pdf = client.get("/api/reports/summary.pdf")
        assert resp_pdf.status_code == 400
        assert resp_pdf.json()["detail"] == "No report data available. Run reconciliation first."
