"""Development seed script.

Creates the initial Master configuration, a couple of Loan Types, one ADMIN
account, and an optional demo CLIENT account. Safe to run multiple times -
every insert is guarded by an existence check.

Usage:
    venv\\Scripts\\activate
    python seed.py
"""

from decimal import Decimal

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.admin_profile import AdminProfile
from app.models.approval_fee_rule import ApprovalFeeRule
from app.models.client_profile import ClientProfile
from app.models.duration_rule import DurationRule
from app.models.enums import CalculationFrequency, RepaymentFrequencyCode, UserRole
from app.models.loan_type import LoanType
from app.models.penalty_rule import PenaltyRule
from app.models.repayment_frequency import RepaymentFrequency
from app.models.user import User
from app.services import account_service

PENALTY_DEFAULTS = {
    RepaymentFrequencyCode.MONTHLY: (CalculationFrequency.DAILY, Decimal("1.00")),
    RepaymentFrequencyCode.QUARTERLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
    RepaymentFrequencyCode.HALF_YEARLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
    RepaymentFrequencyCode.YEARLY: (CalculationFrequency.WEEKLY, Decimal("2.00")),
}

LOAN_TYPES = [
    dict(
        name="Personal Loan",
        description="Unsecured loan for personal expenses",
        interest_rate=Decimal("12.00"),
        min_amount=Decimal("10000"),
        max_amount=Decimal("500000"),
    ),
    dict(
        name="Home Improvement Loan",
        description="Financing for renovation and repair work",
        interest_rate=Decimal("10.50"),
        min_amount=Decimal("50000"),
        max_amount=Decimal("1500000"),
    ),
    dict(
        name="Vehicle Loan",
        description="Financing for a new or used vehicle purchase",
        interest_rate=Decimal("9.75"),
        min_amount=Decimal("50000"),
        max_amount=Decimal("2000000"),
    ),
]


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(DurationRule).first() is None:
            db.add(DurationRule(minimum_months=2, maximum_months=36))

        if db.query(ApprovalFeeRule).first() is None:
            db.add(ApprovalFeeRule(minimum_fee_percent=Decimal("0"), maximum_fee_percent=Decimal("5")))

        frequency_by_code: dict[RepaymentFrequencyCode, RepaymentFrequency] = {}
        for code in RepaymentFrequencyCode:
            frequency = db.query(RepaymentFrequency).filter_by(code=code).first()
            if frequency is None:
                frequency = RepaymentFrequency(code=code, is_active=True)
                db.add(frequency)
                db.flush()
            frequency_by_code[code] = frequency

        for code, (calculation_frequency, rate) in PENALTY_DEFAULTS.items():
            frequency = frequency_by_code[code]
            existing = db.query(PenaltyRule).filter_by(repayment_frequency_id=frequency.id).first()
            if existing is None:
                db.add(
                    PenaltyRule(
                        repayment_frequency_id=frequency.id,
                        calculation_frequency=calculation_frequency,
                        penalty_rate=rate,
                        is_active=True,
                    )
                )

        if db.query(LoanType).count() == 0:
            db.add_all(LoanType(is_active=True, **fields) for fields in LOAN_TYPES)

        admin_user = db.query(User).filter_by(email="admin@loanms.com").first()
        if admin_user is None:
            admin_user = User(
                email="admin@loanms.com",
                password_hash=hash_password("Admin@12345"),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
            db.flush()
            db.add(AdminProfile(user_id=admin_user.id, employee_id="EMP0001", name="System Administrator"))

        dev_client_user = db.query(User).filter_by(email="client@loanms.com").first()
        if dev_client_user is None:
            dev_client_user = User(
                email="client@loanms.com",
                password_hash=hash_password("Client@12345"),
                role=UserRole.CLIENT,
            )
            db.add(dev_client_user)
            db.flush()
            client_profile = ClientProfile(
                user_id=dev_client_user.id, name="Demo Client", phone="9990001111", credit_score=720
            )
            db.add(client_profile)
            db.flush()
            account_service.create_virtual_account(db, client_profile)

        db.commit()
        print("Seed data created/verified successfully.")
        print("Admin login:  admin@loanms.com / Admin@12345")
        print("Client login: client@loanms.com / Client@12345")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
