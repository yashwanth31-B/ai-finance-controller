"""
Authentication & Role-Based Access Control Service
===================================================
Handles password hashing (bcrypt via passlib), JWT token generation & verification,
seed account initialization, and FastAPI dependency injection security guards.
"""

import os
import uuid
import datetime
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal, get_db
from models import UserDB

SECRET_KEY = os.environ.get("JWT_SECRET", "ai-finance-controller-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

DEMO_USERS = [
    {
        "user_id": "usr-admin-01",
        "email": "admin@finance.ai",
        "name": "System Administrator",
        "password": "Admin@123",
        "role": "ADMIN"
    },
    {
        "user_id": "usr-reviewer-01",
        "email": "reviewer@finance.ai",
        "name": "Finance Reviewer",
        "password": "Reviewer@123",
        "role": "REVIEWER"
    },
    {
        "user_id": "usr-viewer-01",
        "email": "viewer@finance.ai",
        "name": "Auditor Viewer",
        "password": "Viewer@123",
        "role": "VIEWER"
    }
]


def hash_password(password: str) -> str:
    """Hash plaintext password securely using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Encodes JWT access token with user claims and expiration."""
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None


def seed_demo_users(db: Session = None) -> None:
    """Ensures default demo user accounts exist in database upon startup."""
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        for demo in DEMO_USERS:
            existing = db.query(UserDB).filter(UserDB.email == demo["email"]).first()
            if not existing:
                user = UserDB(
                    user_id=demo["user_id"],
                    email=demo["email"],
                    name=demo["name"],
                    hashed_password=hash_password(demo["password"]),
                    role=demo["role"]
                )
                db.add(user)
        db.commit()
    finally:
        if close_db:
            db.close()


def authenticate_user(email: str, password: str, db: Session) -> Optional[UserDB]:
    """Authenticates user email and password against database."""
    seed_demo_users(db=db)
    user = db.query(UserDB).filter(UserDB.email == email.strip().lower()).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserDB:
    """Dependency returning authenticated UserDB record or raising HTTP 401."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing or invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_email = payload["sub"]
    user = db.query(UserDB).filter(UserDB.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(allowed_roles: list[str]):
    """Factory creating dependency that checks user role against allowed list."""
    def role_checker(current_user: UserDB = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden for role '{current_user.role}'. Required role: {allowed_roles}."
            )
        return current_user
    return role_checker
