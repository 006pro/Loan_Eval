from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ApplicationStatus, RepaymentFrequencyCode
from app.models.mixins import TimestampMixin


class LoanApplication(Base, TimestampMixin):
    __tablename__ = "loan_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), nullable=False, index=True)
    loan_type_id: Mapped[int] = mapped_column(ForeignKey("loan_types.id"), nullable=False)
    requested_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    requested_duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_frequency: Mapped[RepaymentFrequencyCode] = mapped_column(
        Enum(RepaymentFrequencyCode, native_enum=False, length=20), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.SUBMITTED,
        nullable=False,
    )
    rejection_reason: Mapped[str | None] = mapped_column(String(500))
    submitted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime)

    client: Mapped["ClientProfile"] = relationship()
    loan_type: Mapped["LoanType"] = relationship()
    evaluation: Mapped["LoanEvaluation | None"] = relationship(
        back_populates="loan_application", uselist=False, cascade="all, delete-orphan"
    )
    loan: Mapped["Loan | None"] = relationship(
        back_populates="application", uselist=False, cascade="all, delete-orphan"
    )
