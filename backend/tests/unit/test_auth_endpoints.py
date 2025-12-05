"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    """Ensure we can register a brand new user."""
    payload = {
        "email": "integration-user@example.com",
        "password": "SecurePass123!",
        "first_name": "Integration",
        "last_name": "User",
    }
    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]


def test_register_duplicate_email(client: TestClient):
    """Registering with an existing email should fail."""
    payload = {
        "email": "duplicate-user@example.com",
        "password": "SecurePass123!",
        "first_name": "Duplicate",
        "last_name": "User",
    }

    response_first = client.post("/api/v1/auth/register", json=payload)
    assert response_first.status_code == 200

    response_second = client.post("/api/v1/auth/register", json=payload)
    assert response_second.status_code == 400
    assert "already exists" in response_second.json()["detail"]


def test_login_with_registered_user(client: TestClient):
    """User can login after successful registration."""
    email = "login-user@example.com"
    password = "SecurePass123!"
    register_payload = {
        "email": email,
        "password": password,
        "first_name": "Login",
        "last_name": "User",
    }
    response_register = client.post("/api/v1/auth/register", json=register_payload)
    assert response_register.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login-json", json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"


def test_login_with_invalid_credentials(client: TestClient):
    """Invalid credentials should be rejected."""
    payload = {
        "email": "invalid-login@example.com",
        "password": "SecurePass123!",
        "first_name": "Invalid",
        "last_name": "Login",
    }
    response_register = client.post("/api/v1/auth/register", json=payload)
    assert response_register.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login-json",
        json={"email": payload["email"], "password": "WrongPassword!"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Incorrect email or password"


def test_form_login_with_invalid_credentials(client: TestClient):
    """Form-based login should also reject invalid credentials."""
    payload = {
        "email": "invalid-form-login@example.com",
        "password": "SecurePass123!",
        "first_name": "Invalid",
        "last_name": "FormLogin",
    }
    response_register = client.post("/api/v1/auth/register", json=payload)
    assert response_register.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": "WrongPassword!"},
    )
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Incorrect email or password"


@pytest.mark.parametrize("password_length", [8, 72, 73, 128, 512])
def test_register_and_login_with_varied_password_lengths(client: TestClient, password_length: int):
    """Registration and login should work for passwords across and beyond bcrypt limits."""
    email = f"long-pass-{password_length}@example.com"
    password = "A" * password_length
    payload = {
        "email": email,
        "password": password,
        "first_name": f"Long{password_length}",
        "last_name": "Password",
    }

    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200, register_response.text

    login_json_response = client.post(
        "/api/v1/auth/login-json", json={"email": email, "password": password}
    )
    assert login_json_response.status_code == 200, login_json_response.text
    json_data = login_json_response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

    login_form_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_form_response.status_code == 200, login_form_response.text
    form_data = login_form_response.json()
    assert "access_token" in form_data
    assert form_data["token_type"] == "bearer"


def test_register_and_login_with_unicode_password(client: TestClient):
    """Unicode passwords (multi-byte, >72 bytes) should register and login successfully."""
    password = "复杂密码🚀" * 25  # Multi-byte password exceeding 72-byte bcrypt limit
    email = "unicode-pass@example.com"
    payload = {
        "email": email,
        "password": password,
        "first_name": "Unicode",
        "last_name": "User",
    }

    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 200, register_response.text

    login_response = client.post(
        "/api/v1/auth/login-json",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
