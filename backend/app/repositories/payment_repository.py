from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


def list_by_loan(db: Session, loan_id: int) -> list[Payment]:
    return list(db.execute(select(Payment).where(Payment.loan_id == loan_id).order_by(Payment.id)).scalars())
