from fastapi.testclient import TestClient


def test_admin_can_list_and_view_loans(client: TestClient, admin_headers: dict[str, str], active_loan: dict) -> None:
    listing = client.get("/api/v1/admin/loans", headers=admin_headers)
    assert listing.status_code == 200
    assert any(loan["id"] == active_loan["id"] for loan in listing.json())

    detail = client.get(f"/api/v1/admin/loans/{active_loan['id']}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "ACTIVE"

    schedule = client.get(f"/api/v1/admin/loans/{active_loan['id']}/schedule", headers=admin_headers)
    assert schedule.status_code == 200
    assert len(schedule.json()) == 12


def test_client_cannot_access_admin_loans(client: TestClient, client_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/admin/loans", headers=client_headers)
    assert response.status_code == 403
