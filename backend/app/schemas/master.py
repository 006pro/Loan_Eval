from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import CalculationFrequency, RepaymentFrequencyCode


class DurationRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    minimum_months: int
    maximum_months: int


class DurationRuleUpdate(BaseModel):
    minimum_months: int = Field(ge=1)
    maximum_months: int = Field(ge=1)

    @field_validator("maximum_months")
    @classmethod
    def _check_range(cls, value: int, info) -> int:
        minimum = info.data.get("minimum_months")
        if minimum is not None and value < minimum:
            raise ValueError("maximum_months must be greater than or equal to minimum_months")
        return value


class ApprovalFeeRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    minimum_fee_percent: Decimal
    maximum_fee_percent: Decimal


class ApprovalFeeRuleUpdate(BaseModel):
    minimum_fee_percent: Decimal = Field(ge=0, le=100)
    maximum_fee_percent: Decimal = Field(ge=0, le=100)

    @field_validator("maximum_fee_percent")
    @classmethod
    def _check_range(cls, value: Decimal, info) -> Decimal:
        minimum = info.data.get("minimum_fee_percent")
        if minimum is not None and value < minimum:
            raise ValueError("maximum_fee_percent must be greater than or equal to minimum_fee_percent")
        return value


class LoanTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    interest_rate: Decimal
    min_amount: Decimal
    max_amount: Decimal
    is_active: bool


class LoanTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    interest_rate: Decimal = Field(gt=0, le=100)
    min_amount: Decimal = Field(gt=0)
    max_amount: Decimal = Field(gt=0)

    @field_validator("max_amount")
    @classmethod
    def _check_amount_range(cls, value: Decimal, info) -> Decimal:
        minimum = info.data.get("min_amount")
        if minimum is not None and value < minimum:
            raise ValueError("max_amount must be greater than or equal to min_amount")
        return value


class LoanTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    interest_rate: Decimal | None = Field(default=None, gt=0, le=100)
    min_amount: Decimal | None = Field(default=None, gt=0)
    max_amount: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class RepaymentFrequencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: RepaymentFrequencyCode
    is_active: bool


class RepaymentFrequencyUpdate(BaseModel):
    is_active: bool


class PenaltyRuleOut(BaseModel):
    id: int
    repayment_frequency: RepaymentFrequencyCode
    calculation_frequency: CalculationFrequency
    penalty_rate: Decimal
    is_active: bool


class PenaltyRuleUpdate(BaseModel):
    penalty_rate: Decimal = Field(ge=0, le=100)
    is_active: bool | None = None


class ApplicationConfigOut(BaseModel):
    """Everything a client needs to render the loan application form,
    read live from Master configuration rather than hardcoded."""

    minimum_duration_months: int
    maximum_duration_months: int
    active_repayment_frequencies: list[RepaymentFrequencyCode]
