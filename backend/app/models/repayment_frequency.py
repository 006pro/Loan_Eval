from sqlalchemy import Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import RepaymentFrequencyCode
from app.models.mixins import TimestampMixin


class RepaymentFrequency(Base, TimestampMixin):
    __tablename__ = "repayment_frequencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[RepaymentFrequencyCode] = mapped_column(
        Enum(RepaymentFrequencyCode, native_enum=False, length=20), unique=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
