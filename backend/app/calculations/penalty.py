from decimal import Decimal, ROUND_HALF_UP

from app.models.enums import CalculationFrequency

TWO_PLACES = Decimal("0.01")


def calculate_penalty(
    overdue_amount: Decimal,
    overdue_days: int,
    penalty_rate: Decimal,
    calculation_frequency: CalculationFrequency,
) -> Decimal:
    if overdue_days <= 0:
        return Decimal("0.00")

    if calculation_frequency == CalculationFrequency.DAILY:
        units = Decimal(overdue_days)
    else:
        units = Decimal(overdue_days) / Decimal(7)

    amount = overdue_amount * (penalty_rate / Decimal(100)) * units
    return amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
