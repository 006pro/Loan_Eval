from decimal import Decimal, ROUND_HALF_UP

from app.models.enums import RepaymentFrequencyCode

TWO_PLACES = Decimal("0.01")

FREQUENCY_MONTHS: dict[RepaymentFrequencyCode, int] = {
    RepaymentFrequencyCode.MONTHLY: 1,
    RepaymentFrequencyCode.QUARTERLY: 3,
    RepaymentFrequencyCode.HALF_YEARLY: 6,
    RepaymentFrequencyCode.YEARLY: 12,
}


def number_of_installments(duration_months: int, frequency: RepaymentFrequencyCode) -> int:
    months_per_period = FREQUENCY_MONTHS[frequency]
    return -(-duration_months // months_per_period)  # ceil division


def period_interest_rate(annual_rate: Decimal, frequency: RepaymentFrequencyCode) -> Decimal:
    months_per_period = FREQUENCY_MONTHS[frequency]
    return (annual_rate / Decimal(100)) * Decimal(months_per_period) / Decimal(12)


def calculate_emi(
    principal: Decimal, annual_rate: Decimal, duration_months: int, frequency: RepaymentFrequencyCode
) -> Decimal:
    n = number_of_installments(duration_months, frequency)
    r = period_interest_rate(annual_rate, frequency)

    if r == 0:
        emi = principal / Decimal(n)
    else:
        factor = (1 + r) ** n
        emi = principal * r * factor / (factor - 1)

    return emi.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
