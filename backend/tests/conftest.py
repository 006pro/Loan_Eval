from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.admin_profile import AdminProfile
from app.models.approval_fee_rule import ApprovalFeeRule
from app.models.duration_rule import DurationRule
from app.models.enums import CalculationFrequency, RepaymentFrequencyCode, UserRole
from app.models.penalty_rule import PenaltyRule
from app.models.repayment_frequency import RepaymentFrequency
from app.models.user import User

TEST_DATABASE_URL = get_settings().database_url.rsplit("/", 1)[0] + "/loan_management_test"


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL, future=True)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine) -> Session:
    """A session bound to a SAVEPOINT so that application-level `commit()` calls
    (used throughout the service layer for real transactional behavior) never
    escape the outer transaction, which is always rolled back after the test."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    TestSessionLocal = sessionmaker(bind=connection, autoflush=False, autocommit=False, future=True)
    session = TestSessionLocal()
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    _seed_master_data(session)
    session.commit()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


def _seed_master_data(session: Session) -> None:
    session.add(DurationRule(minimum_months=2, maximum_months=36))
    session.add(ApprovalFeeRule(minimum_fee_percent=Decimal("0"), maximum_fee_percent=Decimal("5")))

    penalty_defaults = {
        RepaymentFrequencyCode.MONTHLY: (CalculationFrequency.DAILY, Decimal("1.00")),
        RepaymentFrequencyCode.QUARTERLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
        RepaymentFrequencyCode.HALF_YEARLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
        RepaymentFrequencyCode.YEARLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
    }
    for code, (calc_frequency, rate) in penalty_defaults.items():
        frequency = RepaymentFrequency(code=code, is_active=True)
        session.add(frequency)
        session.flush()
        session.add(
            PenaltyRule(
                repayment_frequency_id=frequency.id,
                calculation_frequency=calc_frequency,
                penalty_rate=rate,
                is_active=True,
            )
        )

    admin_user = User(email="admin@example.com", password_hash=hash_password("Admin@12345"), role=UserRole.ADMIN)
    session.add(admin_user)
    session.flush()
    session.add(AdminProfile(user_id=admin_user.id, employee_id="EMP0001", name="Test Admin"))


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    response = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "Admin@12345"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def client_token(client: TestClient) -> str:
    client.post(
        "/api/v1/auth/register",
        json={"email": "client@example.com", "password": "StrongPass123", "name": "Test Client"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": "client@example.com", "password": "StrongPass123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def client_headers(client_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {client_token}"}


@pytest.fixture()
def completed_client_headers(client: TestClient, client_headers: dict[str, str]) -> dict[str, str]:
    response = client.put(
        "/api/v1/clients/me",
        json={
            "phone": "9876543210",
            "address": "221B Baker Street",
            "monthly_income": "60000",
            "credit_score": 720,
        },
        headers=client_headers,
    )
    assert response.status_code == 200
    return client_headers


@pytest.fixture()
def active_loan_type_id(client: TestClient, admin_headers: dict[str, str]) -> int:
    response = client.post(
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
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture()
def active_loan(
    client: TestClient,
    admin_headers: dict[str, str],
    completed_client_headers: dict[str, str],
    active_loan_type_id: int,
) -> dict:
    """Submits, approves, and fee-pays a loan so it is ACTIVE with a generated schedule."""
    application = client.post(
        "/api/v1/loan-applications",
        json={
            "loan_type_id": active_loan_type_id,
            "requested_amount": "100000",
            "requested_duration_months": 12,
            "requested_frequency": "MONTHLY",
        },
        headers=completed_client_headers,
    ).json()

    client.post(
        f"/api/v1/admin/loan-applications/{application['id']}/approve",
        json={"approved_amount": "100000", "approval_fee_percent": "2.5", "credit_score": 720},
        headers=admin_headers,
    )

    loans_list = client.get("/api/v1/loans", headers=completed_client_headers).json()
    loan = loans_list[0]

    pay_fee_response = client.post(f"/api/v1/loans/{loan['id']}/fee/pay", headers=completed_client_headers)
    assert pay_fee_response.status_code == 200
    return pay_fee_response.json()
