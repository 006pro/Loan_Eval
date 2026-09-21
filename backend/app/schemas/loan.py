from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import FeeStatus, LoanStatus, RepaymentFrequencyCode, ScheduleStatus


class LoanFeeOut(BaseModel):
    id: int
    fee_percentage: Decimal
    fee_amount: Decimal
    status: FeeStatus
    calculated_at: datetime
    paid_at: datetime | None


class LoanOut(BaseModel):
    id: int
    application_id: int
    loan_type_id: int
    loan_type_name: str
    approved_amount: Decimal
    interest_rate: Decimal
    duration_months: int
    repayment_frequency: RepaymentFrequencyCode
    emi_amount: Decimal
    outstanding_principal: Decimal
    start_date: date | None
    end_date: date | None
    status: LoanStatus
    fee: LoanFeeOut | None


class RepaymentScheduleOut(BaseModel):
    id: int
    installment_number: int
    due_date: date
    opening_principal: Decimal
    scheduled_principal: Decimal
    scheduled_interest: Decimal
    scheduled_amount: Decimal
    paid_principal: Decimal
    paid_interest: Decimal
    paid_amount: Decimal
    remaining_principal: Decimal
    status: ScheduleStatus
    paid_at: datetime | None
