from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ScheduleStatus
from app.models.repayment_schedule import RepaymentSchedule


def create_many(db: Session, rows: list[RepaymentSchedule]) -> list[RepaymentSchedule]:
    db.add_all(rows)
    db.flush()
    return rows


def list_by_loan(db: Session, loan_id: int) -> list[RepaymentSchedule]:
    return list(
        db.execute(
            select(RepaymentSchedule)
            .where(RepaymentSchedule.loan_id == loan_id)
            .order_by(RepaymentSchedule.installment_number)
        ).scalars()
    )


def get_next_payable(db: Session, loan_id: int) -> RepaymentSchedule | None:
    return db.execute(
        select(RepaymentSchedule)
        .where(
            RepaymentSchedule.loan_id == loan_id,
            RepaymentSchedule.status.in_([ScheduleStatus.PENDING, ScheduleStatus.OVERDUE]),
        )
        .order_by(RepaymentSchedule.installment_number)
        .limit(1)
        .with_for_update()
    ).scalar_one_or_none()


def list_pending_or_overdue(db: Session, loan_id: int) -> list[RepaymentSchedule]:
    return list(
        db.execute(
            select(RepaymentSchedule)
            .where(
                RepaymentSchedule.loan_id == loan_id,
                RepaymentSchedule.status.in_([ScheduleStatus.PENDING, ScheduleStatus.OVERDUE]),
            )
            .order_by(RepaymentSchedule.installment_number)
            .with_for_update()
        ).scalars()
    )


def count_overdue(db: Session, loan_id: int) -> int:
    return len(
        list(
            db.execute(
                select(RepaymentSchedule.id).where(
                    RepaymentSchedule.loan_id == loan_id, RepaymentSchedule.status == ScheduleStatus.OVERDUE
                )
            )
        )
    )
