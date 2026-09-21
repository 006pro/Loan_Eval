from fastapi.testclient import TestClient


def test_admin_can_list_audit_logs(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert response.status_code == 200
    logs = response.json()
    assert any(log["action"] == "LOGIN" for log in logs)


def test_client_cannot_list_audit_logs(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/admin/audit-logs", headers=client_headers)
    assert response.status_code == 403


def test_master_duration_change_does_not_affect_existing_loan(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> None:
    application = client.post(
        "/api/v1/loan-applications",
        json={
            "loan_type_id": active_loan_type_id,
            "requested_amount": "100000",
            "requested_duration_months": 24,
            "requested_frequency": "MONTHLY",
        },
        headers=completed_client_headers,
    ).json()

    approve = client.post(
        f"/api/v1/admin/loan-applications/{application['id']}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "2.5", "credit_score": 700},
        headers=admin_headers,
    )
    assert approve.status_code == 200
    loan_id = approve.json()["id"]

    # Change the Master duration and fee rules after the loan was approved.
    client.put(
        "/api/v1/admin/master/duration",
        json={"minimum_months": 1, "maximum_months": 60},
        headers=admin_headers,
    )
    client.put(
        "/api/v1/admin/master/fees",
        json={"minimum_fee_percent": "0", "maximum_fee_percent": "10"},
        headers=admin_headers,
    )

    # The existing loan must keep the values that were actually used at approval time.
    loan = client.get(f"/api/v1/loans/{loan_id}", headers=completed_client_headers).json()
    assert loan["duration_months"] == 24
    assert loan["fee"]["fee_percentage"] == "2.50"

    # A brand new application may now use the widened range.
    new_application = client.post(
        "/api/v1/loan-applications",
        json={
            "loan_type_id": active_loan_type_id,
            "requested_amount": "100000",
            "requested_duration_months": 48,
            "requested_frequency": "MONTHLY",
        },
        headers=completed_client_headers,
    )
    assert new_application.status_code == 201

    new_approve = client.post(
        f"/api/v1/admin/loan-applications/{new_application.json()['id']}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "7", "credit_score": 700},
        headers=admin_headers,
    )
    assert new_approve.status_code == 200
    assert new_approve.json()["duration_months"] == 48
    assert new_approve.json()["fee"]["fee_percentage"] == "7.00"
