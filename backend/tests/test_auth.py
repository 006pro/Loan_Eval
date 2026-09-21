from fastapi.testclient import TestClient


def test_register_creates_client_with_funded_account(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "client1@example.com", "password": "StrongPass123", "name": "Asha Rao"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "CLIENT"
    assert body["access_token"]


def test_register_duplicate_email_rejected(client: TestClient) -> None:
    payload = {"email": "dup@example.com", "password": "StrongPass123", "name": "Dup User"}
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_login_success(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "StrongPass123", "name": "Login User"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "StrongPass123"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "CLIENT"


def test_login_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "whatever123"}
    )
    assert response.status_code == 401
