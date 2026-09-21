from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EvaluationDecision


class LoanEvaluation(Base):
    __tablename__ = "loan_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_application_id: Mapped[int] = mapped_column(
        ForeignKey("loan_applications.id"), unique=True, nullable=False
    )
    admin_id: Mapped[int] = mapped_column(ForeignKey("admin_profiles.id"), nullable=False)
    credit_score: Mapped[int | None] = mapped_column(Integer)
    decision: Mapped[EvaluationDecision] = mapped_column(
        Enum(EvaluationDecision, native_enum=False, length=20), nullable=False
    )
    remarks: Mapped[str | None] = mapped_column(String(500))
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    loan_application: Mapped["LoanApplication"] = relationship(back_populates="evaluation")
    admin: Mapped["AdminProfile"] = relationship()
