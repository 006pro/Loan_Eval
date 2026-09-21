from fastapi.testclient import TestClient


def test_admin_can_read_duration_rule(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/admin/master/duration", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == {"minimum_months": 2, "maximum_months": 36}


def test_admin_can_update_duration_rule(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.put(
        "/api/v1/admin/master/duration",
        json={"minimum_months": 1, "maximum_months": 60},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json() == {"minimum_months": 1, "maximum_months": 60}


def test_duration_rule_rejects_max_below_min(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.put(
        "/api/v1/admin/master/duration",
        json={"minimum_months": 10, "maximum_months": 5},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_admin_can_update_fee_rule(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.put(
        "/api/v1/admin/master/fees",
        json={"minimum_fee_percent": "0", "maximum_fee_percent": "10"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["maximum_fee_percent"] == "10.00"


def test_fee_rule_rejects_max_below_min(client: TestClient, admin_headers: dict[str, str]) -> None:
    response = client.put(
        "/api/v1/admin/master/fees",
        json={"minimum_fee_percent": "5", "maximum_fee_percent": "1"},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_client_cannot_access_admin_master(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/admin/master/duration", headers=client_headers)
    assert response.status_code == 403


def test_unauthenticated_cannot_access_admin_master(client: TestClient) -> None:
    response = client.get("/api/v1/admin/master/duration")
    assert response.status_code == 401


def test_admin_can_create_and_list_loan_types(client: TestClient, admin_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/api/v1/admin/master/loan-types",
        json={
            "name": "Personal Loan",
            "description": "Unsecured personal loan",
            "interest_rate": "12.00",
            "min_amount": "10000",
            "max_amount": "500000",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    loan_type_id = create_response.json()["id"]

    public_list = client.get("/api/v1/loan-types")
    assert public_list.status_code == 200
    assert any(lt["id"] == loan_type_id for lt in public_list.json())

    deactivate = client.put(
        f"/api/v1/admin/master/loan-types/{loan_type_id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert deactivate.status_code == 200
    assert deactivate.json()["is_active"] is False

    public_list_after = client.get("/api/v1/loan-types")
    assert all(lt["id"] != loan_type_id for lt in public_list_after.json())


def test_admin_can_list_and_update_penalty_rules(client: TestClient, admin_headers: dict[str, str]) -> None:
    listing = client.get("/api/v1/admin/master/penalties", headers=admin_headers)
    assert listing.status_code == 200
    rules = listing.json()
    assert len(rules) == 4
    monthly_rule = next(r for r in rules if r["repayment_frequency"] == "MONTHLY")
    assert monthly_rule["calculation_frequency"] == "DAILY"

    update = client.put(
        f"/api/v1/admin/master/penalties/{monthly_rule['id']}",
        json={"penalty_rate": "1.50"},
        headers=admin_headers,
    )
    assert update.status_code == 200
    assert update.json()["penalty_rate"] == "1.50"
