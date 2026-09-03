import os
import sys
import pytest
from fastapi.testclient import TestClient

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app
from services.auth import seed_demo_users, verify_password, hash_password

client = TestClient(app)


def test_login_success():
    """Verify POST /api/auth/login returns valid access token and user info for seeded admin."""
    response = client.post("/api/auth/login", json={
        "email": "admin@finance.ai",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@finance.ai"
    assert data["user"]["role"] == "ADMIN"


def test_login_failure():
    """Verify POST /api/auth/login rejects invalid credentials with 401."""
    response = client.post("/api/auth/login", json={
        "email": "admin@finance.ai",
        "password": "WrongPassword123"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_auth_me_protected():
    """Verify GET /api/auth/me returns authenticated user profile with valid Bearer token."""
    login_resp = client.post("/api/auth/login", json={
        "email": "reviewer@finance.ai",
        "password": "Reviewer@123"
    })
    token = login_resp.json()["access_token"]

    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    user_data = me_resp.json()
    assert user_data["email"] == "reviewer@finance.ai"
    assert user_data["role"] == "REVIEWER"


def test_auth_me_unauthorized():
    """Verify GET /api/auth/me returns 401 without valid Bearer header."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_password_hashing():
    """Verify bcrypt hashing generates non-plaintext hashed string and verifies correctly."""
    plain = "SuperSecret123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongSecret", hashed) is False
