from fastapi import APIRouter, HTTPException
from schemas import AssistantQueryRequest, AssistantQueryResponse
from services.assistant import answer_finance_question

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/query", response_model=AssistantQueryResponse)
def query_finance_assistant(payload: AssistantQueryRequest):
    """
    Queries current reconciliation batch data, operational KPIs, and exceptions cache.
    Returns structured answer, related invoice IDs, and data sources used.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question prompt cannot be empty.")

    try:
        return answer_finance_question(payload.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Assistant query failed: {str(exc)}")
