import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from main import app

client = TestClient(app)


def test_metrics_api_endpoint():
    """Verify GET /api/metrics returns correct schema and KPI values."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()

    assert "total_records" in data
    assert "automatically_matched" in data
    assert "needs_review" in data
    assert "exceptions" in data
    assert "match_rate" in data
    assert "verified_accuracy" in data
    assert "throughput" in data
    assert "average_confidence" in data
    assert "reconciliation_status" in data
    assert "exception_breakdown" in data
    assert "scenario_performance" in data

    assert isinstance(data["total_records"], int)
    assert isinstance(data["match_rate"], float)
    assert isinstance(data["verified_accuracy"], float)
    assert isinstance(data["throughput"], float)
    assert isinstance(data["scenario_performance"], list)
