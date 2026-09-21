from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import LoanStatus
from app.models.loan import Loan
from app.models.loan_fee import LoanFee


def create_loan(db: Session, loan: Loan) -> Loan:
    db.add(loan)
    db.flush()
    return loan


def create_fee(db: Session, fee: LoanFee) -> LoanFee:
    db.add(fee)
    db.flush()
    return fee


def get_by_id(db: Session, loan_id: int) -> Loan | None:
    return db.execute(
        select(Loan)
        .options(joinedload(Loan.loan_type), joinedload(Loan.fee), joinedload(Loan.schedule))
        .where(Loan.id == loan_id)
    ).unique().scalar_one_or_none()


def get_locked_by_id(db: Session, loan_id: int) -> Loan | None:
    return db.execute(select(Loan).where(Loan.id == loan_id).with_for_update()).scalar_one_or_none()


def list_by_client(db: Session, client_id: int) -> list[Loan]:
    return list(
        db.execute(
            select(Loan)
            .options(joinedload(Loan.loan_type))
            .where(Loan.client_id == client_id)
            .order_by(Loan.id.desc())
        ).scalars()
    )


def list_all(db: Session, *, loan_status: LoanStatus | None = None) -> list[Loan]:
    stmt = (
        select(Loan)
        .options(joinedload(Loan.loan_type), joinedload(Loan.client))
        .order_by(Loan.id.desc())
    )
    if loan_status is not None:
        stmt = stmt.where(Loan.status == loan_status)
    return list(db.execute(stmt).scalars())
