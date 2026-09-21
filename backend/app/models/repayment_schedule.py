from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ScheduleStatus
from app.models.mixins import TimestampMixin


class RepaymentSchedule(Base, TimestampMixin):
    __tablename__ = "repayment_schedules"
    __table_args__ = (UniqueConstraint("loan_id", "installment_number", name="uq_loan_installment"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    installment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    opening_principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    scheduled_principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    scheduled_interest: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    scheduled_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    paid_principal: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    paid_interest: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    remaining_principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus, native_enum=False, length=20), default=ScheduleStatus.PENDING, nullable=False
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)

    loan: Mapped["Loan"] = relationship(back_populates="schedule")
