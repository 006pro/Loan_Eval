from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import FeeStatus
from app.models.mixins import TimestampMixin


class LoanFee(Base, TimestampMixin):
    __tablename__ = "loan_fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"), unique=True, nullable=False)
    fee_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    fee_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[FeeStatus] = mapped_column(
        Enum(FeeStatus, native_enum=False, length=20), default=FeeStatus.PENDING, nullable=False
    )
    calculated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)

    loan: Mapped["Loan"] = relationship(back_populates="fee")
