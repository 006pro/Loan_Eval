from fastapi.testclient import TestClient


def _submit_application(client: TestClient, headers: dict[str, str], loan_type_id: int) -> int:
    response = client.post(
        "/api/v1/loan-applications",
        json={
            "loan_type_id": loan_type_id,
            "requested_amount": "100000",
            "requested_duration_months": 12,
            "requested_frequency": "MONTHLY",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_admin_can_list_and_view_application(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)

    listing = client.get("/api/v1/admin/loan-applications", headers=admin_headers)
    assert listing.status_code == 200
    assert any(a["id"] == application_id for a in listing.json())

    detail = client.get(f"/api/v1/admin/loan-applications/{application_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["client"]["name"] == "Test Client"


def test_approve_creates_loan_in_pending_fee_status(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)

    response = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "2.5", "credit_score": 720},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PENDING_FEE"
    assert body["fee"]["fee_amount"] == "2500.00"
    assert body["interest_rate"] == "12.00"


def test_approve_rejects_fee_above_master_maximum(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)

    response = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "7", "credit_score": 700},
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_reject_requires_nonempty_reason(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)

    response = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/reject",
        json={"rejection_reason": ""},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_reject_reason_visible_to_client(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)

    reject_response = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/reject",
        json={"rejection_reason": "Insufficient repayment capacity"},
        headers=admin_headers,
    )
    assert reject_response.status_code == 200

    client_view = client.get(f"/api/v1/loan-applications/{application_id}", headers=completed_client_headers)
    assert client_view.status_code == 200
    body = client_view.json()
    assert body["status"] == "REJECTED"
    assert body["rejection_reason"] == "Insufficient repayment capacity"


def test_cannot_evaluate_application_twice(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)
    client.post(
        f"/api/v1/admin/loan-applications/{application_id}/reject",
        json={"rejection_reason": "Not eligible"},
        headers=admin_headers,
    )
    second = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "2.5"},
        headers=admin_headers,
    )
    assert second.status_code == 400


def test_client_cannot_approve_application(
    client: TestClient,
    client_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application_id = _submit_application(client, completed_client_headers, active_loan_type_id)
    response = client.post(
        f"/api/v1/admin/loan-applications/{application_id}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "2.5"},
        headers=client_headers,
    )
    assert response.status_code == 403
