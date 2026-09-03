"""
Platform Settings & Reconciliation Rules Service
=================================================
Manages persistent system configuration for reconciliation thresholds and matching tolerances in SQLite.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from database import SessionLocal
from models import SystemSettings

DEFAULT_SETTINGS = {
    "amount_tolerance": 0.0,
    "date_tolerance_days": 3,
    "auto_match_threshold": 90.0,
    "review_threshold": 70.0,
    "fuzzy_similarity_threshold": 70.0,
    "candidate_score_gap": 10.0,
}


def validate_settings_dict(data: Dict[str, Any]) -> None:
    """
    Validates settings configuration inputs against strict business logic boundaries.
    Raises ValueError with user-friendly error message if validation fails.
    """
    amt_tol = data.get("amount_tolerance")
    if amt_tol is None or amt_tol < 0:
        raise ValueError("Amount difference tolerance cannot be negative.")

    date_tol = data.get("date_tolerance_days")
    if date_tol is None or date_tol < 0:
        raise ValueError("Date window tolerance days cannot be negative.")

    auto_thresh = data.get("auto_match_threshold")
    if auto_thresh is None or auto_thresh < 0 or auto_thresh > 100:
        raise ValueError("Auto-match threshold must be between 0 and 100.")

    rev_thresh = data.get("review_threshold")
    if rev_thresh is None or rev_thresh < 0 or rev_thresh > 100:
        raise ValueError("Review threshold must be between 0 and 100.")

    if auto_thresh <= rev_thresh:
        raise ValueError("Auto-match threshold must be strictly greater than review threshold.")

    fuzzy_thresh = data.get("fuzzy_similarity_threshold")
    if fuzzy_thresh is None or fuzzy_thresh < 0 or fuzzy_thresh > 100:
        raise ValueError("Fuzzy similarity threshold must be between 0 and 100.")

    cand_gap = data.get("candidate_score_gap")
    if cand_gap is None or cand_gap < 0:
        raise ValueError("Candidate score gap cannot be negative.")


def get_active_settings(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Retrieves current active system settings from database.
    Initializes default settings row if no settings exist.
    """
    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        settings_db = db.query(SystemSettings).first()
        if not settings_db:
            settings_db = SystemSettings(**DEFAULT_SETTINGS)
            db.add(settings_db)
            db.commit()
            db.refresh(settings_db)

        return {
            "amount_tolerance": float(settings_db.amount_tolerance),
            "date_tolerance_days": int(settings_db.date_tolerance_days),
            "auto_match_threshold": float(settings_db.auto_match_threshold),
            "review_threshold": float(settings_db.review_threshold),
            "fuzzy_similarity_threshold": float(settings_db.fuzzy_similarity_threshold),
            "candidate_score_gap": float(settings_db.candidate_score_gap),
            "updated_at": settings_db.updated_at.isoformat() if settings_db.updated_at else datetime.utcnow().isoformat()
        }
    finally:
        if close_db_session:
            db.close()


def update_active_settings(data: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Validates and updates system settings in database.
    Returns updated settings dictionary.
    """
    validate_settings_dict(data)

    close_db_session = False
    if db is None:
        db = SessionLocal()
        close_db_session = True

    try:
        settings_db = db.query(SystemSettings).first()
        if not settings_db:
            settings_db = SystemSettings()
            db.add(settings_db)

        settings_db.amount_tolerance = float(data["amount_tolerance"])
        settings_db.date_tolerance_days = int(data["date_tolerance_days"])
        settings_db.auto_match_threshold = float(data["auto_match_threshold"])
        settings_db.review_threshold = float(data["review_threshold"])
        settings_db.fuzzy_similarity_threshold = float(data["fuzzy_similarity_threshold"])
        settings_db.candidate_score_gap = float(data["candidate_score_gap"])
        settings_db.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(settings_db)

        return {
            "amount_tolerance": float(settings_db.amount_tolerance),
            "date_tolerance_days": int(settings_db.date_tolerance_days),
            "auto_match_threshold": float(settings_db.auto_match_threshold),
            "review_threshold": float(settings_db.review_threshold),
            "fuzzy_similarity_threshold": float(settings_db.fuzzy_similarity_threshold),
            "candidate_score_gap": float(settings_db.candidate_score_gap),
            "updated_at": settings_db.updated_at.isoformat() if settings_db.updated_at else datetime.utcnow().isoformat()
        }
    finally:
        if close_db_session:
            db.close()


def reset_active_settings(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Restores system settings to safe defaults.
    """
    return update_active_settings(DEFAULT_SETTINGS, db=db)
