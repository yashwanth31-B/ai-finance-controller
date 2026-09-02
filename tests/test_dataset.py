import os
import sys
import csv
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from scripts.generate_data import generate_all_datasets, get_project_paths, RANDOM_SEED

client = TestClient(app)

_, DATA_DIR = get_project_paths()
INVOICES_CSV = os.path.join(DATA_DIR, "invoices.csv")
BANK_CSV = os.path.join(DATA_DIR, "bank_transactions.csv")
GATEWAY_CSV = os.path.join(DATA_DIR, "gateway_transactions.csv")
GROUND_TRUTH_CSV = os.path.join(DATA_DIR, "ground_truth.csv")


def read_csv_rows(file_path: str):
    """Utility to read header and data rows from a CSV file."""
    assert os.path.exists(file_path), f"File missing: {file_path}"
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    return fieldnames, rows


def test_csv_files_exist():
    """Verify all 4 required CSV files exist in data directory."""
    assert os.path.exists(INVOICES_CSV), "data/invoices.csv missing"
    assert os.path.exists(BANK_CSV), "data/bank_transactions.csv missing"
    assert os.path.exists(GATEWAY_CSV), "data/gateway_transactions.csv missing"
    assert os.path.exists(GROUND_TRUTH_CSV), "data/ground_truth.csv missing"


def test_invoice_count_and_uniqueness():
    """Verify at least 100 invoices exist and all invoice_ids are unique."""
    fieldnames, rows = read_csv_rows(INVOICES_CSV)
    
    # Required fields verification
    expected_fields = [
        "invoice_id", "customer_id", "customer_name", "invoice_number",
        "amount", "currency", "invoice_date", "due_date", "reference", "status"
    ]
    for field in expected_fields:
        assert field in fieldnames, f"Missing required column in invoices.csv: {field}"

    assert len(rows) >= 100, f"Expected at least 100 invoices, found {len(rows)}"
    
    invoice_ids = [row["invoice_id"] for row in rows]
    assert len(invoice_ids) == len(set(invoice_ids)), "Duplicate invoice_ids found in invoices.csv"


def test_ground_truth_parity_and_scenarios():
    """Verify ground_truth.csv has exactly 1 row per invoice and includes required scenario types."""
    _, invoices = read_csv_rows(INVOICES_CSV)
    _, ground_truth = read_csv_rows(GROUND_TRUTH_CSV)

    assert len(ground_truth) == len(invoices), (
        f"Ground truth row count ({len(ground_truth)}) does not match invoice count ({len(invoices)})"
    )

    invoice_ids_in_invoices = set(r["invoice_id"] for r in invoices)
    invoice_ids_in_ground_truth = set(r["invoice_id"] for r in ground_truth)
    assert invoice_ids_in_invoices == invoice_ids_in_ground_truth, "Mismatch between invoice_ids in invoices.csv and ground_truth.csv"

    # Verify scenario types exist
    scenarios = set(r["scenario_type"] for r in ground_truth)
    expected_scenarios = {
        "exact_match",
        "customer_name_variation",
        "payment_date_variation",
        "amount_mismatch",
        "duplicate_payment",
        "missing_payment",
        "gateway_fee",
        "ambiguous_match",
        "reference_mismatch",
        "currency_mismatch"
    }
    for scenario in expected_scenarios:
        assert scenario in scenarios, f"Missing scenario type in ground_truth.csv: {scenario}"


def test_reproducibility_with_seed(tmp_path):
    """Verify generated dataset is completely reproducible using fixed seed."""
    tmp_dir = str(tmp_path)
    stats1 = generate_all_datasets(data_dir=tmp_dir, seed=RANDOM_SEED)

    # Read generated rows from run 1
    with open(os.path.join(tmp_dir, "invoices.csv"), "r", encoding="utf-8") as f:
        rows1 = f.read()

    # Run 2
    stats2 = generate_all_datasets(data_dir=tmp_dir, seed=RANDOM_SEED)
    with open(os.path.join(tmp_dir, "invoices.csv"), "r", encoding="utf-8") as f:
        rows2 = f.read()

    assert stats1 == stats2, "Stats mismatch across identical seed runs"
    assert rows1 == rows2, "CSV content mismatch across identical seed runs"


def test_demo_data_stats_endpoint():
    """Verify GET /api/demo-data/stats returns 200 and matches actual file record counts."""
    response = client.get("/api/demo-data/stats")
    assert response.status_code == 200
    data = response.json()

    _, invoices = read_csv_rows(INVOICES_CSV)
    _, bank_txns = read_csv_rows(BANK_CSV)
    _, gateway_txns = read_csv_rows(GATEWAY_CSV)
    _, ground_truth = read_csv_rows(GROUND_TRUTH_CSV)

    assert data["invoice_records"] == len(invoices)
    assert data["bank_records"] == len(bank_txns)
    assert data["gateway_records"] == len(gateway_txns)
    assert data["ground_truth_records"] == len(ground_truth)
