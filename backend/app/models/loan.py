from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import LoanStatus, RepaymentFrequencyCode
from app.models.mixins import TimestampMixin


class Loan(Base, TimestampMixin):
    """Frozen at approval time: interest_rate, duration_months and repayment_frequency
    never change afterwards, even if the corresponding Master rules change later."""

    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("loan_applications.id"), unique=True, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    loan_type_id: Mapped[int] = mapped_column(ForeignKey("loan_types.id"), nullable=False)
    approved_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    repayment_frequency: Mapped[RepaymentFrequencyCode] = mapped_column(
        Enum(RepaymentFrequencyCode, native_enum=False, length=20), nullable=False
    )
    emi_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    outstanding_principal: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus, native_enum=False, length=20), default=LoanStatus.PENDING_FEE, nullable=False
    )

    application: Mapped["LoanApplication"] = relationship(back_populates="loan")
    client: Mapped["ClientProfile"] = relationship()
    loan_type: Mapped["LoanType"] = relationship()
    fee: Mapped["LoanFee | None"] = relationship(back_populates="loan", uselist=False, cascade="all, delete-orphan")
    schedule: Mapped[list["RepaymentSchedule"]] = relationship(back_populates="loan", cascade="all, delete-orphan")
