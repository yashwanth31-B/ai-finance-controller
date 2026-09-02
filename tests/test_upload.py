import os
import sys
import io
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app

client = TestClient(app)

# Helper valid CSV strings
VALID_INVOICES_CSV = """invoice_id,customer_name,amount,currency,invoice_date,reference
INV_UP_001,Acme Corp,10000.0,INR,2026-08-01,REF_UP_1
INV_UP_002,Beta LLC,25000.0,INR,2026-08-01,REF_UP_2
"""

VALID_BANK_CSV = """transaction_id,description,amount,currency,transaction_date,reference
BANK_UP_001,ACME CORP REF_UP_1,10000.0,INR,2026-08-01,REF_UP_1
BANK_UP_002,BETA LLC REF_UP_2,25000.0,INR,2026-08-01,REF_UP_2
"""

VALID_GATEWAY_CSV = """payment_id,customer_name,amount,currency,payment_date,reference,gateway,fee,net_amount
PAY_UP_001,Acme Corp,10000.0,INR,2026-08-01,REF_UP_1,Razorpay,200.0,9800.0
PAY_UP_002,Beta LLC,25000.0,INR,2026-08-01,REF_UP_2,Razorpay,500.0,24500.0
"""


def test_valid_three_file_upload():
    """1. Verify valid 3-file CSV upload passes validation and returns upload_batch_id."""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["upload_batch_id"] is not None
    assert data["upload_batch_id"].startswith("upload-")
    assert data["files"]["invoices"]["rows"] == 2
    assert len(data["files"]["invoices"]["preview"]) == 2


def test_missing_invoice_file():
    """2. Verify missing invoice file fails validation."""
    files = {
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["files"]["invoices"]["valid"] is False
    assert "Missing required invoices CSV file" in data["files"]["invoices"]["errors"][0]


def test_missing_bank_file():
    """3. Verify missing bank file fails validation."""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["files"]["bank"]["valid"] is False


def test_missing_gateway_file():
    """4. Verify missing gateway file fails validation."""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["files"]["gateway"]["valid"] is False


def test_wrong_extension():
    """5. Verify unsupported file extension (.png) is rejected."""
    files = {
        "invoices": ("invoices.png", io.BytesIO(b"fake png data"), "image/png"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("Only .csv files" in err for err in data["files"]["invoices"]["errors"])


def test_empty_csv():
    """6. Verify empty 0-byte CSV fails validation."""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(b""), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("is empty" in err for err in data["files"]["invoices"]["errors"])


def test_missing_required_column():
    """7. Verify missing required column ('amount') fails validation."""
    invalid_csv = """invoice_id,customer_name,currency,invoice_date,reference
INV001,Test Corp,INR,2026-08-01,REF001
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(invalid_csv.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("Missing required column: amount" in err for err in data["files"]["invoices"]["errors"])


def test_invalid_amount():
    """8. Verify non-numeric amount ('abc') fails validation."""
    invalid_csv = """invoice_id,customer_name,amount,currency,invoice_date,reference
INV001,Test Corp,abc,INR,2026-08-01,REF001
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(invalid_csv.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("invalid amount values" in err for err in data["files"]["invoices"]["errors"])


def test_invalid_date():
    """9. Verify invalid date string fails validation."""
    invalid_csv = """invoice_id,customer_name,amount,currency,invoice_date,reference
INV001,Test Corp,10000.0,INR,invalid-date-format,REF001
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(invalid_csv.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("invalid invoice_date values" in err for err in data["files"]["invoices"]["errors"])


def test_duplicate_invoice_id():
    """10. Verify duplicate invoice_id fails validation."""
    dup_csv = """invoice_id,customer_name,amount,currency,invoice_date,reference
INV001,Acme,10000.0,INR,2026-08-01,REF01
INV001,Acme Dup,10000.0,INR,2026-08-01,REF02
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(dup_csv.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("Duplicate invoice_id detected: INV001" in err for err in data["files"]["invoices"]["errors"])


def test_duplicate_bank_transaction_id():
    """11. Verify duplicate bank transaction_id fails validation."""
    dup_csv = """transaction_id,description,amount,currency,transaction_date,reference
BANK001,Desc 1,10000.0,INR,2026-08-01,REF01
BANK001,Desc 2,10000.0,INR,2026-08-01,REF02
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(dup_csv.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("Duplicate transaction_id detected: BANK001" in err for err in data["files"]["bank"]["errors"])


def test_duplicate_gateway_payment_id():
    """12. Verify duplicate gateway payment_id fails validation."""
    dup_csv = """payment_id,customer_name,amount,currency,payment_date,reference
PAY001,Acme,10000.0,INR,2026-08-01,REF01
PAY001,Acme Dup,10000.0,INR,2026-08-01,REF02
"""
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(dup_csv.encode()), "text/csv"),
    }
    response = client.post("/api/upload/validate", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert any("Duplicate payment_id detected: PAY001" in err for err in data["files"]["gateway"]["errors"])


def test_uploaded_reconciliation_uses_existing_engine():
    """13. Verify POST /api/reconciliation/run-uploaded runs reconciliation using existing engine."""
    # First upload & validate
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    val_resp = client.post("/api/upload/validate", files=files)
    batch_id = val_resp.json()["upload_batch_id"]

    # Run uploaded batch reconciliation
    run_resp = client.post("/api/reconciliation/run-uploaded", json={"upload_batch_id": batch_id})
    assert run_resp.status_code == 200
    summary = run_resp.json()
    assert summary["total_records"] == 2
    assert summary["matched"] == 2


def test_uploaded_batch_does_not_overwrite_demo_data():
    """14. Verify uploaded CSV files do not overwrite synthetic demo files in data/."""
    demo_invoice_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "invoices.csv"))
    with open(demo_invoice_path, "r", encoding="utf-8") as f:
        demo_content_before = f.read()

    # Upload custom batch
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    client.post("/api/upload/validate", files=files)

    with open(demo_invoice_path, "r", encoding="utf-8") as f:
        demo_content_after = f.read()

    assert demo_content_before == demo_content_after


def test_verified_accuracy_is_null_when_ground_truth_missing():
    """15. Verify metrics return verified_accuracy=None and ground_truth_available=False for uploaded datasets without ground_truth.csv."""
    # Upload and run custom uploaded batch
    files = {
        "invoices": ("invoices.csv", io.BytesIO(VALID_INVOICES_CSV.encode()), "text/csv"),
        "bank": ("bank_transactions.csv", io.BytesIO(VALID_BANK_CSV.encode()), "text/csv"),
        "gateway": ("gateway_transactions.csv", io.BytesIO(VALID_GATEWAY_CSV.encode()), "text/csv"),
    }
    val_resp = client.post("/api/upload/validate", files=files)
    batch_id = val_resp.json()["upload_batch_id"]
    client.post("/api/reconciliation/run-uploaded", json={"upload_batch_id": batch_id})

    # Query metrics
    metrics_resp = client.get("/api/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["ground_truth_available"] is False
    assert metrics["verified_accuracy"] is None
