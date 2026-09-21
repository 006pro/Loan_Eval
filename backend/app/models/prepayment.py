from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Prepayment(Base):
    __tablename__ = "prepayments"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False)
    account_transaction_id: Mapped[int] = mapped_column(ForeignKey("account_transactions.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    principal_reduction: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    loan: Mapped["Loan"] = relationship()
    account_transaction: Mapped["AccountTransaction"] = relationship()
