import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify GET / returns correct application name and running status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Finance Controller"
    assert data["status"] == "running"


def test_health_endpoint():
    """Verify GET /api/health returns healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_headers():
    """Verify CORS headers are enabled for frontend communication."""
    response = client.get("/", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
