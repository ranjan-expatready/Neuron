"""Shared configuration for TestSprite login/tests."""
import os

API_BASE_URL = os.getenv("TESTSPRITE_API_BASE_URL", "http://localhost:8000")
UI_BASE_URL = os.getenv("TESTSPRITE_UI_BASE_URL", "http://localhost:3000")

LOGIN_JSON_ENDPOINT = "/api/v1/auth/login-json"

TEST_USER_EMAIL = os.getenv("TESTSPRITE_USER_EMAIL", "testsprite.automation@canadaos.dev")
TEST_USER_PASSWORD = os.getenv("TESTSPRITE_USER_PASSWORD", "TestSprite!234")
INVALID_TEST_PASSWORD = os.getenv("TESTSPRITE_INVALID_PASSWORD", "WrongPassword123!")

REQUEST_TIMEOUT = int(os.getenv("TESTSPRITE_REQUEST_TIMEOUT", "30"))
