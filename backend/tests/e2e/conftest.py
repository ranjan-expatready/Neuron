"""
Playwright fixtures and configuration for E2E tests.
"""
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Browser launch arguments for Playwright."""
    return {
        "headless": True,
        "slow_mo": 100,  # Slow down operations for visibility
    }


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def frontend_url():
    """Frontend URL for E2E tests."""
    return "http://localhost:3000"


@pytest.fixture
def authenticated_page(page: Page, base_url: str) -> Page:
    """
    Create an authenticated page session.

    This fixture logs in a test user and returns a page with authentication cookies.
    """
    # Navigate to login page
    page.goto(f"{base_url}/api/v1/auth/login")

    # Login (adjust based on your actual login flow)
    # This is a placeholder - update with actual login logic
    # page.fill('input[name="email"]', "test@example.com")
    # page.fill('input[name="password"]', "test123")
    # page.click('button[type="submit"]')
    # page.wait_for_url("**/dashboard")  # Wait for redirect after login

    return page


@pytest.fixture
def api_client(base_url: str):
    """Create an API client for E2E tests."""
    import httpx

    return httpx.Client(base_url=base_url, timeout=30.0)
