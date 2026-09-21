from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ApprovalFeeRule(Base, TimestampMixin):
    """Singleton master row controlling the allowed approval fee percentage range."""

    __tablename__ = "approval_fee_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    minimum_fee_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    maximum_fee_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
