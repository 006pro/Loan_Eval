from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ClientProfile(Base, TimestampMixin):
    __tablename__ = "client_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(255))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    employment: Mapped[str | None] = mapped_column(String(150))
    monthly_income: Mapped[float | None] = mapped_column(Numeric(14, 2))
    yearly_income: Mapped[float | None] = mapped_column(Numeric(14, 2))
    existing_loans: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bank_account_number: Mapped[str | None] = mapped_column(String(30))
    credit_score: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="client_profile")
    virtual_account: Mapped["VirtualAccount | None"] = relationship(
        back_populates="client", uselist=False, cascade="all, delete-orphan"
    )
