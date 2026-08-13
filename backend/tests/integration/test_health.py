# tests/integration/test_health.py

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check_returns_healthy():
    """Verify health endpoint returns 200 OK and expected payload."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_middleware_attaches_headers():
    """Verify custom middleware generates process time and request ID headers."""
    response = client.get("/api/v1/health")

    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
    assert response.headers["X-Process-Time"].endswith("ms")


def test_middleware_preserves_incoming_request_id():
    """Verify middleware respects an incoming client X-Request-ID for correlation."""
    custom_request_id = "client-trace-id-999"
    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": custom_request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_request_id