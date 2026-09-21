from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import every model so Alembic autogenerate and Base.metadata see them all.
from app.models import (  # noqa: E402,F401
    account_transaction,
    admin_profile,
    approval_fee_rule,
    audit_log,
    client_profile,
    duration_rule,
    loan,
    loan_application,
    loan_evaluation,
    loan_fee,
    loan_type,
    payment,
    penalty,
    penalty_rule,
    prepayment,
    repayment_frequency,
    repayment_schedule,
    user,
    virtual_account,
)
