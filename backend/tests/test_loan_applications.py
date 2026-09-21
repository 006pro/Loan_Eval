from fastapi.testclient import TestClient


def _valid_payload(loan_type_id: int) -> dict:
    return {
        "loan_type_id": loan_type_id,
        "requested_amount": "100000",
        "requested_duration_months": 12,
        "requested_frequency": "MONTHLY",
    }


def test_application_config_reflects_master_duration(
    client: TestClient, completed_client_headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/loan-applications/config", headers=completed_client_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["minimum_duration_months"] == 2
    assert body["maximum_duration_months"] == 36
    assert "MONTHLY" in body["active_repayment_frequencies"]


def test_preview_returns_backend_calculated_figures(
    client: TestClient, completed_client_headers: dict[str, str], active_loan_type_id: int
) -> None:
    response = client.post(
        "/api/v1/loan-applications/preview",
        json=_valid_payload(active_loan_type_id),
        headers=completed_client_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["estimated_installment_amount"] == "8884.88"
    assert body["number_of_installments"] == 12


def test_submit_application_success(
    client: TestClient, completed_client_headers: dict[str, str], active_loan_type_id: int
) -> None:
    response = client.post(
        "/api/v1/loan-applications", json=_valid_payload(active_loan_type_id), headers=completed_client_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "SUBMITTED"

    listing = client.get("/api/v1/loan-applications", headers=completed_client_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    detail = client.get(f"/api/v1/loan-applications/{body['id']}", headers=completed_client_headers)
    assert detail.status_code == 200


def test_submit_rejects_incomplete_profile(
    client: TestClient, client_headers: dict[str, str], active_loan_type_id: int
) -> None:
    response = client.post(
        "/api/v1/loan-applications", json=_valid_payload(active_loan_type_id), headers=client_headers
    )
    assert response.status_code == 400


def test_submit_rejects_amount_outside_loan_type_range(
    client: TestClient, completed_client_headers: dict[str, str], active_loan_type_id: int
) -> None:
    payload = _valid_payload(active_loan_type_id)
    payload["requested_amount"] = "999999999"
    response = client.post("/api/v1/loan-applications", json=payload, headers=completed_client_headers)
    assert response.status_code == 400


def test_submit_rejects_duration_outside_master_range(
    client: TestClient, completed_client_headers: dict[str, str], active_loan_type_id: int
) -> None:
    payload = _valid_payload(active_loan_type_id)
    payload["requested_duration_months"] = 100
    response = client.post("/api/v1/loan-applications", json=payload, headers=completed_client_headers)
    assert response.status_code == 400


def test_submit_rejects_inactive_loan_type(
    client: TestClient,
    completed_client_headers: dict[str, str],
    admin_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    client.put(
        f"/api/v1/admin/master/loan-types/{active_loan_type_id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    response = client.post(
        "/api/v1/loan-applications", json=_valid_payload(active_loan_type_id), headers=completed_client_headers
    )
    assert response.status_code == 400


def test_client_cannot_view_another_clients_application(client: TestClient, admin_headers: dict[str, str]) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "StrongPass123", "name": "Owner"},
    )
    owner_login = client.post(
        "/api/v1/auth/login", json={"email": "owner@example.com", "password": "StrongPass123"}
    )
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}
    client.put(
        "/api/v1/clients/me",
        json={"phone": "1112223333", "address": "Somewhere", "monthly_income": "40000"},
        headers=owner_headers,
    )
    loan_type = client.post(
        "/api/v1/admin/master/loan-types",
        json={
            "name": "Vehicle Loan",
            "interest_rate": "9.00",
            "min_amount": "10000",
            "max_amount": "500000",
        },
        headers=admin_headers,
    ).json()
    created = client.post(
        "/api/v1/loan-applications", json=_valid_payload(loan_type["id"]), headers=owner_headers
    )
    assert created.status_code == 201
    application_id = created.json()["id"]

    client.post(
        "/api/v1/auth/register",
        json={"email": "intruder@example.com", "password": "StrongPass123", "name": "Intruder"},
    )
    intruder_login = client.post(
        "/api/v1/auth/login", json={"email": "intruder@example.com", "password": "StrongPass123"}
    )
    intruder_headers = {"Authorization": f"Bearer {intruder_login.json()['access_token']}"}

    response = client.get(f"/api/v1/loan-applications/{application_id}", headers=intruder_headers)
    assert response.status_code == 404
