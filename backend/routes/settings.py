from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import SettingsResponse, SettingsUpdateRequest
from services.settings import (
    get_active_settings,
    update_active_settings,
    reset_active_settings
)

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def fetch_settings(db: Session = Depends(get_db)):
    """Retrieves current platform settings and reconciliation rule tolerances."""
    return get_active_settings(db=db)


@router.put("", response_model=SettingsResponse)
def modify_settings(payload: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """
    Updates platform settings and reconciliation rules.
    Validates input ranges and threshold relationships.
    """
    try:
        updated = update_active_settings(payload.model_dump(), db=db)
        return updated
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/reset", response_model=SettingsResponse)
def restore_default_settings(db: Session = Depends(get_db)):
    """Restores platform settings to safe default parameters."""
    return reset_active_settings(db=db)
