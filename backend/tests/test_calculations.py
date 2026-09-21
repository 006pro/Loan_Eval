from datetime import date
from decimal import Decimal

from app.calculations.emi import calculate_emi, number_of_installments
from app.calculations.fee import calculate_fee_amount
from app.calculations.penalty import calculate_penalty
from app.calculations.repayment import generate_schedule, summarize
from app.models.enums import CalculationFrequency, RepaymentFrequencyCode


def test_emi_matches_known_reducing_balance_value() -> None:
    # Principal 100000, annual rate 12%, 12 monthly installments -> well known EMI ~8884.88
    emi = calculate_emi(Decimal("100000"), Decimal("12"), 12, RepaymentFrequencyCode.MONTHLY)
    assert emi == Decimal("8884.88")


def test_emi_zero_interest_splits_evenly() -> None:
    emi = calculate_emi(Decimal("12000"), Decimal("0"), 12, RepaymentFrequencyCode.MONTHLY)
    assert emi == Decimal("1000.00")


def test_number_of_installments_rounds_up_for_uneven_duration() -> None:
    assert number_of_installments(10, RepaymentFrequencyCode.QUARTERLY) == 4


def test_schedule_fully_amortizes_to_zero() -> None:
    rows = generate_schedule(
        Decimal("100000"), Decimal("12"), 12, RepaymentFrequencyCode.MONTHLY, date(2026, 1, 1)
    )
    assert len(rows) == 12
    assert rows[-1].closing_principal == Decimal("0.00")
    total_principal = sum((row.principal_component for row in rows), Decimal("0.00"))
    assert total_principal == Decimal("100000.00")


def test_schedule_summary_totals() -> None:
    rows = generate_schedule(
        Decimal("100000"), Decimal("12"), 12, RepaymentFrequencyCode.MONTHLY, date(2026, 1, 1)
    )
    total_interest, total_payable = summarize(rows)
    assert total_interest > Decimal("0.00")
    assert total_payable == Decimal("100000.00") + total_interest


def test_fee_calculation() -> None:
    assert calculate_fee_amount(Decimal("500000"), Decimal("2.5")) == Decimal("12500.00")


def test_penalty_daily() -> None:
    amount = calculate_penalty(Decimal("10000"), 5, Decimal("1"), CalculationFrequency.DAILY)
    assert amount == Decimal("500.00")


def test_penalty_weekly() -> None:
    amount = calculate_penalty(Decimal("10000"), 14, Decimal("2"), CalculationFrequency.WEEKLY)
    assert amount == Decimal("400.00")


def test_penalty_no_overdue_days_is_zero() -> None:
    assert calculate_penalty(Decimal("10000"), 0, Decimal("1"), CalculationFrequency.DAILY) == Decimal("0.00")
