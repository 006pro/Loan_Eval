from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import ApplicationStatus, RepaymentFrequencyCode


class LoanApplicationRequest(BaseModel):
    loan_type_id: int
    requested_amount: Decimal = Field(gt=0)
    requested_duration_months: int = Field(gt=0)
    requested_frequency: RepaymentFrequencyCode


class LoanApplicationPreviewOut(BaseModel):
    loan_type_id: int
    loan_type_name: str
    requested_amount: Decimal
    interest_rate: Decimal
    duration_months: int
    repayment_frequency: RepaymentFrequencyCode
    number_of_installments: int
    estimated_installment_amount: Decimal
    estimated_total_interest: Decimal
    estimated_total_payable: Decimal


class LoanApplicationOut(BaseModel):
    id: int
    loan_type_id: int
    loan_type_name: str
    requested_amount: Decimal
    requested_duration_months: int
    requested_frequency: RepaymentFrequencyCode
    status: ApplicationStatus
    rejection_reason: str | None
    submitted_at: datetime
    evaluated_at: datetime | None
