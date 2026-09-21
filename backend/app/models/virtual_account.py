from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AccountStatus
from app.models.mixins import TimestampMixin


class VirtualAccount(Base, TimestampMixin):
    __tablename__ = "virtual_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client_profiles.id"), unique=True, nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, native_enum=False, length=20), default=AccountStatus.ACTIVE, nullable=False
    )

    client: Mapped["ClientProfile"] = relationship(back_populates="virtual_account")
    transactions: Mapped[list["AccountTransaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
