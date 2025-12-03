"""
Example E2E test using Playwright.

This demonstrates the structure for end-to-end testing.
"""
import os
import re

import pytest
from playwright.sync_api import Page, expect

RUN_E2E = os.getenv("RUN_E2E", "false").lower() in {"1", "true", "yes"}
pytestmark = pytest.mark.skipif(
    not RUN_E2E,
    reason="E2E Playwright tests require RUN_E2E=true plus running backend/frontend services.",
)


@pytest.mark.e2e
@pytest.mark.playwright
class TestAPIHealthCheck:
    """Test API health check endpoint via browser."""

    def test_api_root_endpoint(self, page: Page, base_url: str):
        """Test that API root endpoint is accessible."""
        page.goto(f"{base_url}/")

        # Check page content (API returns JSON, so we check the response)
        response = page.request.get(f"{base_url}/")
        assert response.status == 200

        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_api_health_endpoint(self, page: Page, base_url: str):
        """Test that health check endpoint works."""
        response = page.request.get(f"{base_url}/health")
        assert response.status == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data

    def test_api_docs_accessible(self, page: Page, base_url: str):
        """Test that API documentation is accessible."""
        page.goto(f"{base_url}/docs")

        # Check that docs page loaded (FastAPI Swagger UI)
        expect(page).to_have_title(re.compile("Swagger", re.IGNORECASE))

        # Check for API title
        page_content = page.content()
        assert "Canada Immigration OS" in page_content or "API" in page_content


@pytest.mark.e2e
@pytest.mark.playwright
@pytest.mark.slow
class TestFrontendWorkflows:
    """Test frontend workflows (requires frontend to be running)."""

    @pytest.mark.skip(reason="Requires frontend to be running - enable when ready")
    def test_frontend_homepage(self, page: Page, frontend_url: str):
        """Test that frontend homepage loads."""
        page.goto(frontend_url)

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Check for key elements (adjust based on your frontend)
        # expect(page.locator("h1")).to_be_visible()
