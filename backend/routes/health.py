from fastapi import APIRouter
from schemas import HealthStatusResponse

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health", response_model=HealthStatusResponse)
def get_health_status():
    """Health check endpoint to verify backend service operational status."""
    return {"status": "healthy"}
