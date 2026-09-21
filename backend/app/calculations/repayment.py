import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.calculations.emi import FREQUENCY_MONTHS, calculate_emi, number_of_installments, period_interest_rate
from app.models.enums import RepaymentFrequencyCode

TWO_PLACES = Decimal("0.01")


@dataclass
class ScheduleRow:
    installment_number: int
    due_date: date
    opening_principal: Decimal
    principal_component: Decimal
    interest_component: Decimal
    installment_amount: Decimal
    closing_principal: Decimal


def add_months(start: date, months: int) -> date:
    total_month_index = start.month - 1 + months
    year = start.year + total_month_index // 12
    month = total_month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _amortize(
    principal: Decimal,
    annual_rate: Decimal,
    frequency: RepaymentFrequencyCode,
    due_dates: list[date],
    first_installment_number: int = 1,
) -> list[ScheduleRow]:
    n = len(due_dates)
    if n == 0:
        return []

    step_months = FREQUENCY_MONTHS[frequency]
    r = period_interest_rate(annual_rate, frequency)
    emi = calculate_emi(principal, annual_rate, n * step_months, frequency)

    rows: list[ScheduleRow] = []
    balance = principal
    for offset, due_date in enumerate(due_dates):
        is_last = offset == n - 1
        interest = (balance * r).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        if is_last:
            principal_component = balance
            installment_amount = principal_component + interest
        else:
            principal_component = emi - interest
            installment_amount = emi
        closing = balance - principal_component
        if closing < 0:
            closing = Decimal("0.00")

        rows.append(
            ScheduleRow(
                installment_number=first_installment_number + offset,
                due_date=due_date,
                opening_principal=balance,
                principal_component=principal_component,
                interest_component=interest,
                installment_amount=installment_amount,
                closing_principal=closing,
            )
        )
        balance = closing

    return rows


def generate_schedule(
    principal: Decimal,
    annual_rate: Decimal,
    duration_months: int,
    frequency: RepaymentFrequencyCode,
    start_date: date,
) -> list[ScheduleRow]:
    n = number_of_installments(duration_months, frequency)
    step_months = FREQUENCY_MONTHS[frequency]
    due_dates = [add_months(start_date, step_months * installment_number) for installment_number in range(1, n + 1)]
    return _amortize(principal, annual_rate, frequency, due_dates)


def recompute_schedule(
    principal: Decimal,
    annual_rate: Decimal,
    frequency: RepaymentFrequencyCode,
    due_dates: list[date],
    first_installment_number: int,
) -> list[ScheduleRow]:
    """Re-amortize the still-unpaid installments after a prepayment. Only the rows for
    `due_dates` (already-paid installments are excluded by the caller) are touched."""
    return _amortize(principal, annual_rate, frequency, due_dates, first_installment_number)


def summarize(rows: list[ScheduleRow]) -> tuple[Decimal, Decimal]:
    total_interest = sum((row.interest_component for row in rows), Decimal("0.00"))
    total_payable = sum((row.installment_amount for row in rows), Decimal("0.00"))
    return total_interest, total_payable
