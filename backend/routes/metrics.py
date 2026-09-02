from fastapi import APIRouter
from schemas import MetricsResponse
from services.metrics import compute_metrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse)
def get_operational_metrics():
    """
    Returns live system-wide operational metrics, KPI breakdown,
    verified ground truth accuracy, throughput, and scenario performance statistics.
    """
    return compute_metrics()
