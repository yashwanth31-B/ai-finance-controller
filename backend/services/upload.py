"""
CSV Upload & Validation Service
================================
Validates, parses, checks security limits, and stores uploaded CSV datasets for multi-source reconciliation.
"""

import os
import csv
import io
import uuid
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit per CSV file

REQUIRED_COLUMNS = {
    "invoices": ["invoice_id", "customer_name", "amount", "currency", "invoice_date", "reference"],
    "bank": ["transaction_id", "description", "amount", "currency", "transaction_date", "reference"],
    "gateway": ["payment_id", "customer_name", "amount", "currency", "payment_date", "reference"],
}

ID_FIELDS = {
    "invoices": "invoice_id",
    "bank": "transaction_id",
    "gateway": "payment_id",
}

DATE_FIELDS = {
    "invoices": "invoice_date",
    "bank": "transaction_date",
    "gateway": "payment_date",
}


def get_uploads_dir() -> str:
    """Resolve path to data/uploads directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    uploads_dir = os.path.join(project_root, "data", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir


def parse_date(val: str) -> bool:
    """Checks if a string value can be parsed as a valid date."""
    if not val or not isinstance(val, str):
        return False
    val = val.strip()
    date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%m/%d/%Y"]
    for fmt in date_formats:
        try:
            datetime.strptime(val, fmt)
            return True
        except ValueError:
            pass
    # Try ISO format
    try:
        datetime.fromisoformat(val.replace("Z", "+00:00"))
        return True
    except (ValueError, TypeError):
        pass
    return False


def validate_csv_content(
    file_bytes: bytes,
    filename: str,
    file_type: str
) -> Tuple[bool, List[str], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates CSV file bytes for security, size, schema headers, data types, and duplicate IDs.
    Returns: (is_valid, list_of_errors, full_parsed_rows, preview_10_rows)
    """
    errors: List[str] = []

    # 1. Security Check: File Extension
    ext = os.path.splitext(filename)[1].lower()
    if ext != ".csv":
        errors.append(f"Invalid file extension '{ext}'. Only .csv files are permitted.")
        return False, errors, [], []

    # 2. File Size Check
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        errors.append(f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of 10 MB.")
        return False, errors, [], []

    # 3. Empty File Check
    if not file_bytes or len(file_bytes.strip()) == 0:
        errors.append(f"File '{filename}' is empty.")
        return False, errors, [], []

    # 4. CSV Parsing
    try:
        text_content = file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text_content = file_bytes.decode("latin-1")
        except Exception:
            errors.append(f"Unable to parse {filename} - invalid text encoding.")
            return False, errors, [], []

    try:
        reader = list(csv.DictReader(io.StringIO(text_content)))
    except Exception as exc:
        errors.append(f"Unable to parse {filename}: {str(exc)}")
        return False, errors, [], []

    if not reader:
        errors.append(f"File '{filename}' contains no data rows.")
        return False, errors, [], []

    # 5. Header Schema Validation
    headers = [h.strip() for h in (reader[0].keys() if reader and reader[0] else []) if h]
    required = REQUIRED_COLUMNS.get(file_type, [])
    missing_headers = [req for req in required if req not in headers]
    if missing_headers:
        for m in missing_headers:
            errors.append(f"Missing required column: {m}")
        return False, errors, [], []

    # 6. Row-by-Row Data Validation
    id_field = ID_FIELDS[file_type]
    date_field = DATE_FIELDS[file_type]
    seen_ids = set()
    invalid_dates_count = 0
    invalid_amounts_count = 0

    parsed_rows: List[Dict[str, Any]] = []

    for idx, row in enumerate(reader, start=1):
        clean_row = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}

        # Check Primary ID
        raw_id = clean_row.get(id_field, "")
        if not raw_id:
            errors.append(f"Empty {id_field} detected at row {idx}")
        elif raw_id in seen_ids:
            errors.append(f"Duplicate {id_field} detected: {raw_id}")
        else:
            seen_ids.add(raw_id)

        # Check Amount
        raw_amt = clean_row.get("amount", "")
        try:
            amt_val = float(raw_amt)
            clean_row["amount"] = amt_val
        except (ValueError, TypeError):
            invalid_amounts_count += 1

        # Check Date
        raw_date = clean_row.get(date_field, "")
        if not parse_date(raw_date):
            invalid_dates_count += 1

        parsed_rows.append(clean_row)

    if invalid_amounts_count > 0:
        errors.append(f"{invalid_amounts_count} invalid amount values detected in {filename}")

    if invalid_dates_count > 0:
        errors.append(f"{invalid_dates_count} invalid {date_field} values detected in {filename}")

    is_valid = len(errors) == 0
    preview_rows = parsed_rows[:10]

    return is_valid, errors, parsed_rows, preview_rows


def create_upload_session(
    invoices_bytes: bytes,
    bank_bytes: bytes,
    gateway_bytes: bytes
) -> str:
    """
    Creates an isolated server-side upload directory for the batch and saves validated CSV files.
    Returns: upload_batch_id
    """
    batch_uuid = uuid.uuid4().hex[:8]
    upload_batch_id = f"upload-{batch_uuid}"
    target_dir = os.path.join(get_uploads_dir(), upload_batch_id)
    os.makedirs(target_dir, exist_ok=True)

    with open(os.path.join(target_dir, "invoices.csv"), "wb") as f:
        f.write(invoices_bytes)

    with open(os.path.join(target_dir, "bank_transactions.csv"), "wb") as f:
        f.write(bank_bytes)

    with open(os.path.join(target_dir, "gateway_transactions.csv"), "wb") as f:
        f.write(gateway_bytes)

    return upload_batch_id


def get_upload_batch_dir(upload_batch_id: str) -> Optional[str]:
    """Resolves and validates safety of upload batch directory."""
    if not upload_batch_id or ".." in upload_batch_id or "/" in upload_batch_id or "\\" in upload_batch_id:
        return None
    target_dir = os.path.join(get_uploads_dir(), upload_batch_id)
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        return target_dir
    return None
