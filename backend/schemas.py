from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from datetime import datetime



class RootInfoResponse(BaseModel):
    name: str
    status: str

class HealthStatusResponse(BaseModel):
    status: str

class SystemMetricPlaceholder(BaseModel):
    match_rate: float = 0.0
    verified_accuracy: float = 0.0
    throughput: float = 0.0
    unresolved_exceptions: int = 0


class DemoDataStatsResponse(BaseModel):
    invoice_records: int
    bank_records: int
    gateway_records: int
    ground_truth_records: int


class ReconciliationRunResponse(BaseModel):
    batch_id: str
    total_records: int
    matched: int
    review: int
    exceptions: int
    processing_time_seconds: float
    results_available: bool


class ReconciliationResultItem(BaseModel):
    invoice_id: str
    customer_name: str
    invoice_amount: float
    invoice_date: str
    selected_bank_transaction_id: Optional[str] = None
    selected_gateway_payment_id: Optional[str] = None
    bank_score: float
    gateway_score: float
    overall_confidence_score: float
    status: str
    matched_fields: list[str]
    mismatched_fields: list[str]
    explanation: str
    normalized_customer_name: Optional[str] = None
    fuzzy_customer_score: float = 0.0
    description_similarity: float = 0.0
    best_candidate_score: float = 0.0
    second_best_candidate_score: float = 0.0
    candidate_score_gap: float = 0.0
    matching_method: str = "NO_MATCH"
    exception_id: Optional[str] = None
    exception_type: Optional[str] = None
    severity: Optional[str] = None
    suggested_action: Optional[str] = None


class ExceptionRecord(BaseModel):
    exception_id: str
    batch_id: str
    invoice_id: str
    exception_type: str
    severity: str
    confidence_score: float
    reason: str
    suggested_action: str
    candidate_bank_transaction_ids: list[str]
    candidate_gateway_payment_ids: list[str]
    amount_difference: Optional[float] = None
    percentage_difference: Optional[float] = None
    gross_amount: Optional[float] = None
    fee: Optional[float] = None
    net_amount: Optional[float] = None
    created_at: str
    status: str


class ExceptionSummaryResponse(BaseModel):
    total: int
    open: int
    by_severity: dict[str, int]
    by_type: dict[str, int]


class ScenarioPerformanceItem(BaseModel):
    scenario_name: str
    total_records: int
    correct_results: int
    accuracy: float


class MetricsResponse(BaseModel):
    total_records: int
    automatically_matched: int
    needs_review: int
    exceptions: int
    match_rate: float
    verified_accuracy: Optional[float] = None
    ground_truth_available: bool = True
    throughput: float
    average_confidence: float
    reconciliation_status: dict[str, int]
    exception_breakdown: dict[str, int]
    scenario_performance: list[ScenarioPerformanceItem]


class FileValidationResult(BaseModel):
    filename: str
    rows: int
    valid: bool
    errors: list[str]
    preview: list[dict[str, Any]] = []


class UploadValidationResponse(BaseModel):
    valid: bool
    upload_batch_id: Optional[str] = None
    files: dict[str, FileValidationResult]


class RunUploadedRequest(BaseModel):
    upload_batch_id: str



