from fastapi import APIRouter, HTTPException
from schemas import AIAnalysisRequest, AIAnalysisResponse
from services.ai_assistant import analyze_exception

router = APIRouter(prefix="/api/ai", tags=["ai-assistant"])


@router.post("/analyze-exception", response_model=AIAnalysisResponse)
def analyze_exception_endpoint(payload: AIAnalysisRequest):
    """
    Performs AI-assisted root-cause analysis on an unresolved exception record.
    Returns root-cause summary, confidence score, recommended human action, and financial impact.
    """
    if not payload.invoice_id and not payload.exception_id:
        raise HTTPException(
            status_code=400,
            detail="Either invoice_id or exception_id must be provided for AI analysis."
        )

    try:
        result = analyze_exception(
            invoice_id=payload.invoice_id,
            exception_id=payload.exception_id
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(exc)}")
