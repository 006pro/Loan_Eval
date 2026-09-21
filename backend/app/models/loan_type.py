from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class LoanType(Base, TimestampMixin):
    __tablename__ = "loan_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    interest_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    min_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    max_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
