from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.calculations.penalty import calculate_penalty
from app.models.enums import AuditAction, LoanStatus, PenaltyStatus, ScheduleStatus
from app.models.loan import Loan
from app.models.penalty import Penalty
from app.repositories import master_repository, penalty_repository, schedule_repository
from app.services import audit_service


def assess_loan(db: Session, loan: Loan) -> None:
    """Lazily marks overdue installments and accrues their penalty using the
    Master-configured rate. There is no background scheduler in this system
    (by design), so this runs whenever a loan is read or paid against."""
    if loan.status not in (LoanStatus.ACTIVE, LoanStatus.OVERDUE):
        return

    today = date.today()
    pending_rows = schedule_repository.list_pending_or_overdue(db, loan.id)
    any_overdue = False

    for schedule in pending_rows:
        if schedule.due_date >= today:
            continue
        any_overdue = True
        overdue_days = (today - schedule.due_date).days

        penalty_rule = master_repository.get_penalty_rule_by_frequency_code(db, loan.repayment_frequency)
        if penalty_rule is not None and penalty_rule.is_active:
            penalty_amount = calculate_penalty(
                Decimal(schedule.scheduled_amount),
                overdue_days,
                Decimal(penalty_rule.penalty_rate),
                penalty_rule.calculation_frequency,
            )
            penalty = penalty_repository.get_by_schedule_id(db, schedule.id)
            if penalty is None:
                penalty = Penalty(
                    loan_id=loan.id,
                    schedule_id=schedule.id,
                    overdue_amount=schedule.scheduled_amount,
                    overdue_days=overdue_days,
                    penalty_rate=penalty_rule.penalty_rate,
                    calculation_frequency=penalty_rule.calculation_frequency,
                    penalty_amount=penalty_amount,
                    status=PenaltyStatus.PENDING,
                )
                penalty_repository.create(db, penalty)
                audit_service.record(
                    db,
                    user_id=None,
                    action=AuditAction.PENALTY_CREATED,
                    entity_type="Penalty",
                    entity_id=penalty.id,
                    new_value={"penalty_amount": penalty_amount, "overdue_days": overdue_days},
                )
            elif penalty.status == PenaltyStatus.PENDING:
                penalty.overdue_days = overdue_days
                penalty.penalty_amount = penalty_amount

        schedule.status = ScheduleStatus.OVERDUE

    if any_overdue and loan.status == LoanStatus.ACTIVE:
        loan.status = LoanStatus.OVERDUE
