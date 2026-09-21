from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class DurationRule(Base, TimestampMixin):
    """Singleton master row controlling allowed loan duration (months)."""

    __tablename__ = "duration_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    minimum_months: Mapped[int] = mapped_column(Integer, nullable=False)
    maximum_months: Mapped[int] = mapped_column(Integer, nullable=False)
