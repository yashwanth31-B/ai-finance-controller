import os
import csv
from fastapi import APIRouter, HTTPException
from schemas import DemoDataStatsResponse

router = APIRouter(prefix="/api/demo-data", tags=["demo-data"])


def count_csv_records(file_path: str) -> int:
    """Count data rows in a CSV file, excluding header."""
    if not os.path.exists(file_path):
        return 0
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            next(reader)  # skip header
        except StopIteration:
            return 0
        return sum(1 for row in reader if row and any(cell.strip() for cell in row))


@router.get("/stats", response_model=DemoDataStatsResponse)
def get_demo_data_stats():
    """
    Get record counts from actual generated synthetic dataset CSV files.
    Dynamic counts are read from data/invoices.csv, bank_transactions.csv,
    gateway_transactions.csv, and ground_truth.csv.
    """
    # Resolve data directory path relative to backend routes
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    data_dir = os.path.join(project_root, "data")

    invoices_csv = os.path.join(data_dir, "invoices.csv")
    bank_csv = os.path.join(data_dir, "bank_transactions.csv")
    gateway_csv = os.path.join(data_dir, "gateway_transactions.csv")
    ground_truth_csv = os.path.join(data_dir, "ground_truth.csv")

    return {
        "invoice_records": count_csv_records(invoices_csv),
        "bank_records": count_csv_records(bank_csv),
        "gateway_records": count_csv_records(gateway_csv),
        "ground_truth_records": count_csv_records(ground_truth_csv)
    }
