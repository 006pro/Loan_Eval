from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import AuditAction, LoanStatus, ScheduleStatus
from app.models.loan import Loan
from app.repositories import loan_repository, schedule_repository
from app.schemas.loan import LoanFeeOut, LoanOut, RepaymentScheduleOut
from app.services import audit_service, penalty_service


def to_loan_out(loan: Loan) -> LoanOut:
    fee_out = None
    if loan.fee is not None:
        fee_out = LoanFeeOut(
            id=loan.fee.id,
            fee_percentage=loan.fee.fee_percentage,
            fee_amount=loan.fee.fee_amount,
            status=loan.fee.status,
            calculated_at=loan.fee.calculated_at,
            paid_at=loan.fee.paid_at,
        )
    return LoanOut(
        id=loan.id,
        application_id=loan.application_id,
        loan_type_id=loan.loan_type_id,
        loan_type_name=loan.loan_type.name,
        approved_amount=loan.approved_amount,
        interest_rate=loan.interest_rate,
        duration_months=loan.duration_months,
        repayment_frequency=loan.repayment_frequency,
        emi_amount=loan.emi_amount,
        outstanding_principal=loan.outstanding_principal,
        start_date=loan.start_date,
        end_date=loan.end_date,
        status=loan.status,
        fee=fee_out,
    )


def get_loan_or_404(db: Session, loan_id: int) -> Loan:
    loan = loan_repository.get_by_id(db, loan_id)
    if loan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan not found")
    return loan


def get_client_loan_or_404(db: Session, client_id: int, loan_id: int) -> Loan:
    loan = get_loan_or_404(db, loan_id)
    if loan.client_id != client_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan not found")
    return loan


def list_loans_for_client(db: Session, client_id: int) -> list[LoanOut]:
    return [to_loan_out(loan) for loan in loan_repository.list_by_client(db, client_id)]


def get_client_loan_assessed(db: Session, client_id: int, loan_id: int) -> Loan:
    """Read path that lazily marks overdue installments before returning the loan,
    since this system has no background scheduler to do it proactively."""
    loan = get_client_loan_or_404(db, client_id, loan_id)
    penalty_service.assess_loan(db, loan)
    db.commit()
    return loan


def get_schedule_for_client_loan(db: Session, client_id: int, loan_id: int) -> list[RepaymentScheduleOut]:
    get_client_loan_assessed(db, client_id, loan_id)
    return [
        RepaymentScheduleOut.model_validate(row, from_attributes=True)
        for row in schedule_repository.list_by_loan(db, loan_id)
    ]


def get_fee_for_client_loan(db: Session, client_id: int, loan_id: int) -> LoanFeeOut:
    loan = get_client_loan_or_404(db, client_id, loan_id)
    if loan.fee is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Loan fee not found")
    return LoanFeeOut(
        id=loan.fee.id,
        fee_percentage=loan.fee.fee_percentage,
        fee_amount=loan.fee.fee_amount,
        status=loan.fee.status,
        calculated_at=loan.fee.calculated_at,
        paid_at=loan.fee.paid_at,
    )


def refresh_loan_status_after_payment(db: Session, loan: Loan, user_id: int) -> None:
    """Loan completion is derived from actual financial state, never assumed just
    because a payment endpoint was called."""
    remaining = schedule_repository.list_pending_or_overdue(db, loan.id)
    if loan.outstanding_principal <= 0 and not remaining:
        loan.status = LoanStatus.COMPLETED
        audit_service.record(
            db, user_id=user_id, action=AuditAction.LOAN_COMPLETED, entity_type="Loan", entity_id=loan.id
        )
    elif loan.status == LoanStatus.OVERDUE and not any(row.status == ScheduleStatus.OVERDUE for row in remaining):
        loan.status = LoanStatus.ACTIVE
