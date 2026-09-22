from fastapi.testclient import TestClient


def test_create_admin_requires_admin_auth(client: TestClient) -> None:
    response = client.post(
        "/api/v1/admin/admins",
        json={
            "email": "newadmin@example.com",
            "password": "StrongPass123",
            "name": "New Admin",
            "employee_id": "EMP0002",
        },
    )
    assert response.status_code == 401


def test_create_admin_success(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/admin/admins",
        json={
            "email": "newadmin@example.com",
            "password": "StrongPass123",
            "name": "New Admin",
            "employee_id": "EMP0002",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newadmin@example.com"
    assert body["employee_id"] == "EMP0002"

    login = client.post(
        "/api/v1/auth/login", json={"email": "newadmin@example.com", "password": "StrongPass123"}
    )
    assert login.status_code == 200
    assert login.json()["role"] == "ADMIN"


def test_create_admin_duplicate_email_rejected(client: TestClient, admin_headers: dict[str, str]) -> None:
    payload = {
        "email": "dupadmin@example.com",
        "password": "StrongPass123",
        "name": "Dup Admin",
        "employee_id": "EMP0003",
    }
    first = client.post("/api/v1/admin/admins", json=payload, headers=admin_headers)
    assert first.status_code == 201

    second = client.post(
        "/api/v1/admin/admins",
        json={**payload, "employee_id": "EMP0004"},
        headers=admin_headers,
    )
    assert second.status_code == 409


def test_create_admin_duplicate_employee_id_rejected(client: TestClient, admin_headers: dict[str, str]) -> None:
    payload = {
        "email": "admin-a@example.com",
        "password": "StrongPass123",
        "name": "Admin A",
        "employee_id": "EMP0005",
    }
    first = client.post("/api/v1/admin/admins", json=payload, headers=admin_headers)
    assert first.status_code == 201

    second = client.post(
        "/api/v1/admin/admins",
        json={**payload, "email": "admin-b@example.com"},
        headers=admin_headers,
    )
    assert second.status_code == 409


def test_list_admins_includes_seeded_and_created(client: TestClient, admin_headers: dict[str, str]) -> None:
    client.post(
        "/api/v1/admin/admins",
        json={
            "email": "list-admin@example.com",
            "password": "StrongPass123",
            "name": "List Admin",
            "employee_id": "EMP0007",
        },
        headers=admin_headers,
    )
    response = client.get("/api/v1/admin/admins", headers=admin_headers)
    assert response.status_code == 200
    emails = {row["email"] for row in response.json()}
    assert "admin@example.com" in emails
    assert "list-admin@example.com" in emails


def test_create_admin_rejected_for_client_role(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/admin/admins",
        json={
            "email": "shouldfail@example.com",
            "password": "StrongPass123",
            "name": "Should Fail",
            "employee_id": "EMP0006",
        },
        headers=client_headers,
    )
    assert response.status_code == 403
