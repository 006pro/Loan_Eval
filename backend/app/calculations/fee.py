from decimal import Decimal, ROUND_HALF_UP

TWO_PLACES = Decimal("0.01")


def calculate_fee_amount(approved_amount: Decimal, fee_percentage: Decimal) -> Decimal:
    return (approved_amount * fee_percentage / Decimal(100)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
