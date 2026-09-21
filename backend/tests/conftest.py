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
