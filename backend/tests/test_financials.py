from datetime import date, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import TransactionType
from app.repositories import account_repository


def _client_profile_id(client: TestClient, headers: dict[str, str]) -> int:
    return client.get("/api/v1/clients/me", headers=headers).json()["id"]


def test_fee_payment_activates_loan_and_generates_schedule(active_loan: dict) -> None:
    assert active_loan["status"] == "ACTIVE"
    assert active_loan["fee"]["status"] == "PAID"


def test_schedule_has_expected_number_of_installments(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    response = client.get(f"/api/v1/loans/{active_loan['id']}/schedule", headers=completed_client_headers)
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 12
    assert rows[0]["status"] == "PENDING"


def test_account_reflects_fee_debit_and_disbursement_credit(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    account = client.get("/api/v1/accounts/me", headers=completed_client_headers).json()
    # starter 500000 - fee 2500 + disbursement 100000
    assert account["balance"] == "597500.00"

    transactions = client.get("/api/v1/accounts/me/transactions", headers=completed_client_headers).json()
    types = [t["transaction_type"] for t in transactions]
    assert TransactionType.APPROVAL_FEE_PAYMENT.value in types
    assert TransactionType.LOAN_DISBURSEMENT.value in types


def test_paying_fee_twice_fails(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    response = client.post(f"/api/v1/loans/{active_loan['id']}/fee/pay", headers=completed_client_headers)
    assert response.status_code == 400


def test_emi_payment_reduces_outstanding_principal(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    before = Decimal(active_loan["outstanding_principal"])
    response = client.post(f"/api/v1/loans/{active_loan['id']}/payment", headers=completed_client_headers)
    assert response.status_code == 201
    payment = response.json()
    assert payment["penalty_amount"] == "0.00"

    loan = client.get(f"/api/v1/loans/{active_loan['id']}", headers=completed_client_headers).json()
    after = Decimal(loan["outstanding_principal"])
    assert after == before - Decimal(payment["principal_amount"])

    schedule = client.get(f"/api/v1/loans/{active_loan['id']}/schedule", headers=completed_client_headers).json()
    assert schedule[0]["status"] == "PAID"
    assert schedule[1]["status"] == "PENDING"


def test_full_amortization_completes_loan(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    loan_id = active_loan["id"]
    for _ in range(12):
        response = client.post(f"/api/v1/loans/{loan_id}/payment", headers=completed_client_headers)
        assert response.status_code == 201

    loan = client.get(f"/api/v1/loans/{loan_id}", headers=completed_client_headers).json()
    assert loan["status"] == "COMPLETED"
    assert Decimal(loan["outstanding_principal"]) == Decimal("0.00")

    thirteenth = client.post(f"/api/v1/loans/{loan_id}/payment", headers=completed_client_headers)
    assert thirteenth.status_code == 400


def test_payment_rejected_on_insufficient_balance(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict, db_session: Session
) -> None:
    profile_id = _client_profile_id(client, completed_client_headers)
    account = account_repository.get_by_client_id(db_session, profile_id)
    account.balance = Decimal("10.00")
    db_session.commit()

    response = client.post(f"/api/v1/loans/{active_loan['id']}/payment", headers=completed_client_headers)
    assert response.status_code == 400


def test_prepayment_reduces_principal_and_only_affects_future_installments(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    loan_id = active_loan["id"]

    pay_first = client.post(f"/api/v1/loans/{loan_id}/payment", headers=completed_client_headers)
    assert pay_first.status_code == 201

    schedule_before = client.get(f"/api/v1/loans/{loan_id}/schedule", headers=completed_client_headers).json()
    paid_row_snapshot = schedule_before[0]
    second_installment_before = Decimal(schedule_before[1]["scheduled_amount"])

    prepay = client.post(
        f"/api/v1/loans/{loan_id}/prepayment", json={"amount": "20000"}, headers=completed_client_headers
    )
    assert prepay.status_code == 201

    schedule_after = client.get(f"/api/v1/loans/{loan_id}/schedule", headers=completed_client_headers).json()
    assert schedule_after[0] == paid_row_snapshot  # historical PAID row untouched

    second_installment_after = Decimal(schedule_after[1]["scheduled_amount"])
    assert second_installment_after < second_installment_before

    loan = client.get(f"/api/v1/loans/{loan_id}", headers=completed_client_headers).json()
    assert Decimal(loan["outstanding_principal"]) == Decimal(active_loan["outstanding_principal"]) - Decimal(
        pay_first.json()["principal_amount"]
    ) - Decimal("20000")


def test_prepayment_exceeding_outstanding_principal_rejected(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict
) -> None:
    response = client.post(
        f"/api/v1/loans/{active_loan['id']}/prepayment",
        json={"amount": "999999999"},
        headers=completed_client_headers,
    )
    assert response.status_code == 400


def test_overdue_installment_accrues_penalty_and_is_charged_on_payment(
    client: TestClient, completed_client_headers: dict[str, str], active_loan: dict, db_session: Session
) -> None:
    from app.repositories import schedule_repository

    loan_id = active_loan["id"]
    rows = schedule_repository.list_by_loan(db_session, loan_id)
    rows[0].due_date = date.today() - timedelta(days=10)
    db_session.commit()

    detail = client.get(f"/api/v1/loans/{loan_id}", headers=completed_client_headers).json()
    assert detail["status"] == "OVERDUE"

    schedule = client.get(f"/api/v1/loans/{loan_id}/schedule", headers=completed_client_headers).json()
    assert schedule[0]["status"] == "OVERDUE"

    payment = client.post(f"/api/v1/loans/{loan_id}/payment", headers=completed_client_headers)
    assert payment.status_code == 201
    body = payment.json()
    assert Decimal(body["penalty_amount"]) > Decimal("0.00")

    loan_after = client.get(f"/api/v1/loans/{loan_id}", headers=completed_client_headers).json()
    assert loan_after["status"] == "ACTIVE"


def test_client_cannot_access_another_clients_loan(
    client: TestClient, admin_headers: dict[str, str], active_loan: dict
) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "intruder2@example.com", "password": "StrongPass123", "name": "Intruder"},
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "intruder2@example.com", "password": "StrongPass123"}
    )
    intruder_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/api/v1/loans/{active_loan['id']}", headers=intruder_headers)
    assert response.status_code == 404
