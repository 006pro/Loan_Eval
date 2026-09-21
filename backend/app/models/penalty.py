from sqlalchemy import Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CalculationFrequency, PenaltyStatus
from app.models.mixins import TimestampMixin


class Penalty(Base, TimestampMixin):
    __tablename__ = "penalties"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), nullable=False, index=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("repayment_schedules.id"), nullable=False)
    overdue_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, nullable=False)
    penalty_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    calculation_frequency: Mapped[CalculationFrequency] = mapped_column(
        Enum(CalculationFrequency, native_enum=False, length=20), nullable=False
    )
    penalty_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[PenaltyStatus] = mapped_column(
        Enum(PenaltyStatus, native_enum=False, length=20), default=PenaltyStatus.PENDING, nullable=False
    )

    loan: Mapped["Loan"] = relationship()
    schedule: Mapped["RepaymentSchedule"] = relationship()
