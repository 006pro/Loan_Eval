from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ApplicationStatus, RepaymentFrequencyCode


class ApprovalRequest(BaseModel):
    approved_amount: Decimal = Field(gt=0)
    approval_fee_percent: Decimal = Field(ge=0, le=100)
    credit_score: int | None = Field(default=None, ge=300, le=900)
    remarks: str | None = Field(default=None, max_length=500)


class RejectionRequest(BaseModel):
    rejection_reason: str = Field(min_length=1, max_length=500)
    credit_score: int | None = Field(default=None, ge=300, le=900)
    remarks: str | None = Field(default=None, max_length=500)


class AdminClientSummary(BaseModel):
    id: int
    name: str
    phone: str | None
    monthly_income: Decimal | None
    yearly_income: Decimal | None
    existing_loans: int
    credit_score: int | None


class AdminLoanApplicationOut(BaseModel):
    id: int
    client: AdminClientSummary
    loan_type_id: int
    loan_type_name: str
    interest_rate: Decimal
    requested_amount: Decimal
    requested_duration_months: int
    requested_frequency: RepaymentFrequencyCode
    status: ApplicationStatus
    rejection_reason: str | None
    submitted_at: datetime
    evaluated_at: datetime | None
