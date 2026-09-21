from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PaymentType


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("repayment_schedules.id"), nullable=False)
    account_transaction_id: Mapped[int] = mapped_column(ForeignKey("account_transactions.id"), nullable=False)
    payment_type: Mapped[PaymentType] = mapped_column(
        Enum(PaymentType, native_enum=False, length=20), default=PaymentType.EMI, nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    principal_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    interest_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    penalty_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    payment_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    loan: Mapped["Loan"] = relationship()
    schedule: Mapped["RepaymentSchedule"] = relationship()
    account_transaction: Mapped["AccountTransaction"] = relationship()
