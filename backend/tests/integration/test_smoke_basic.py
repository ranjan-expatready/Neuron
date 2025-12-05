"""
Integration smoke tests ensure critical auth + org flows work end-to-end.
"""

import uuid

import pytest


@pytest.mark.integration
def test_registration_login_and_org_flow(client):
    """
    Register -> login -> create org -> fetch org should succeed using real routes.
    """
    email = f"smoke_{uuid.uuid4().hex}@example.com"
    password = "TestPass!234"

    register_payload = {
        "email": email,
        "password": password,
        "first_name": "Smoke",
        "last_name": "Test",
    }
    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 200
    assert register_response.json()["email"] == email

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    org_payload = {"name": f"Smoke Org {uuid.uuid4().hex[:8]}", "type": "law_firm"}
    org_create_response = client.post("/api/v1/organizations/", json=org_payload, headers=headers)
    assert org_create_response.status_code == 200
    created_org = org_create_response.json()
    assert created_org["name"] == org_payload["name"]

    org_me_response = client.get("/api/v1/organizations/me", headers=headers)
    assert org_me_response.status_code == 200
    org_me = org_me_response.json()
    assert org_me["id"] == created_org["id"]
    assert org_me["subscription_status"] == "active"
