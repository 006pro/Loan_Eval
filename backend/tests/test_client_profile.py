from fastapi.testclient import TestClient


def test_client_can_read_own_profile(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/clients/me", headers=client_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Test Client"
    assert body["email"] == "client@example.com"


def test_client_can_update_own_profile(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.put(
        "/api/v1/clients/me",
        json={"phone": "9876543210", "address": "221B Baker Street", "monthly_income": "60000"},
        headers=client_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["phone"] == "9876543210"
    assert body["monthly_income"] == "60000.00"


def test_unauthenticated_cannot_read_profile(client: TestClient) -> None:
    response = client.get("/api/v1/clients/me")
    assert response.status_code == 401


def test_admin_cannot_use_client_profile_endpoint(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/clients/me", headers=admin_headers)
    assert response.status_code == 403
