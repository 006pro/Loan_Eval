from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import CalculationFrequency
from app.models.mixins import TimestampMixin


class PenaltyRule(Base, TimestampMixin):
    """Master row: one penalty rate per repayment frequency."""

    __tablename__ = "penalty_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    repayment_frequency_id: Mapped[int] = mapped_column(
        ForeignKey("repayment_frequencies.id"), unique=True, nullable=False
    )
    calculation_frequency: Mapped[CalculationFrequency] = mapped_column(
        Enum(CalculationFrequency, native_enum=False, length=20), nullable=False
    )
    penalty_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    repayment_frequency: Mapped["RepaymentFrequency"] = relationship()
