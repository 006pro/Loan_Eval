from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ClientProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    phone: str | None
    address: str | None
    date_of_birth: date | None
    employment: str | None
    monthly_income: Decimal | None
    yearly_income: Decimal | None
    existing_loans: int
    bank_account_number: str | None
    credit_score: int | None
    created_at: datetime
    updated_at: datetime


class ClientProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    employment: str | None = Field(default=None, max_length=150)
    monthly_income: Decimal | None = Field(default=None, ge=0)
    yearly_income: Decimal | None = Field(default=None, ge=0)
    existing_loans: int | None = Field(default=None, ge=0)
    bank_account_number: str | None = Field(default=None, max_length=30)
    credit_score: int | None = Field(default=None, ge=300, le=900)
