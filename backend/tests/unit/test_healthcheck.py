"""
Gold-class unit smoke tests for the FastAPI health endpoint.
"""

import pytest


@pytest.mark.unit
def test_health_endpoint_reports_healthy_status(client):
    """
    The /health route should be fast, dependency-light, and always available.
    """
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"
