import os
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException
from schemas import UploadValidationResponse, FileValidationResult, RunUploadedRequest, ReconciliationRunResponse
from services.upload import (
    validate_csv_content,
    create_upload_session,
    get_upload_batch_dir
)
from services.reconciliation import load_csv_records, run_reconciliation_batch

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload/validate", response_model=UploadValidationResponse)
async def validate_uploaded_files(
    invoices: Optional[UploadFile] = File(None),
    bank: Optional[UploadFile] = File(None),
    gateway: Optional[UploadFile] = File(None)
):
    """
    Validates uploaded Invoice, Bank, and Payment Gateway CSV files.
    Performs security checks, column schema validation, numeric & date verification, and duplicate ID detection.
    Generates preview rows (first 10) and an upload_batch_id if all files are valid.
    """
    file_inputs = {
        "invoices": invoices,
        "bank": bank,
        "gateway": gateway
    }

    file_results = {}
    all_valid = True
    bytes_store = {}

    for key, upload_file in file_inputs.items():
        if not upload_file:
            all_valid = False
            file_results[key] = FileValidationResult(
                filename=f"{key}.csv",
                rows=0,
                valid=False,
                errors=[f"Missing required {key} CSV file."],
                preview=[]
            )
            continue

        try:
            content = await upload_file.read()
            bytes_store[key] = content
            filename = upload_file.filename or f"{key}.csv"

            is_valid, errors, rows, preview = validate_csv_content(content, filename, key)

            if not is_valid:
                all_valid = False

            file_results[key] = FileValidationResult(
                filename=filename,
                rows=len(rows),
                valid=is_valid,
                errors=errors,
                preview=preview
            )
        except Exception as exc:
            all_valid = False
            file_results[key] = FileValidationResult(
                filename=upload_file.filename or f"{key}.csv",
                rows=0,
                valid=False,
                errors=[f"Failed to read file: {str(exc)}"],
                preview=[]
            )

    upload_batch_id = None
    if all_valid and len(bytes_store) == 3:
        upload_batch_id = create_upload_session(
            bytes_store["invoices"],
            bytes_store["bank"],
            bytes_store["gateway"]
        )

    return UploadValidationResponse(
        valid=all_valid,
        upload_batch_id=upload_batch_id,
        files=file_results
    )


@router.post("/reconciliation/run-uploaded", response_model=ReconciliationRunResponse)
def execute_uploaded_reconciliation(payload: RunUploadedRequest):
    """
    Executes 3-way reconciliation on validated uploaded datasets matching upload_batch_id.
    """
    batch_dir = get_upload_batch_dir(payload.upload_batch_id)
    if not batch_dir:
        raise HTTPException(
            status_code=404,
            detail=f"Upload session '{payload.upload_batch_id}' not found or invalid."
        )

    inv_path = os.path.join(batch_dir, "invoices.csv")
    bank_path = os.path.join(batch_dir, "bank_transactions.csv")
    gw_path = os.path.join(batch_dir, "gateway_transactions.csv")

    if not (os.path.exists(inv_path) and os.path.exists(bank_path) and os.path.exists(gw_path)):
        raise HTTPException(
            status_code=400,
            detail="Uploaded batch files are missing or incomplete."
        )

    invoices = load_csv_records(inv_path)
    bank_txns = load_csv_records(bank_path)
    gateway_txns = load_csv_records(gw_path)

    summary, _ = run_reconciliation_batch(invoices, bank_txns, gateway_txns)
    return summary
