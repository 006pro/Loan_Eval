from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentType


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loan_id: int
    schedule_id: int
    payment_type: PaymentType
    amount: Decimal
    principal_amount: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    payment_date: datetime


class PrepaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0)


class PrepaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loan_id: int
    amount: Decimal
    principal_reduction: Decimal
    created_at: datetime
