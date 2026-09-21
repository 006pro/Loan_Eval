from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculations.repayment import recompute_schedule
from app.models.client_profile import ClientProfile
from app.models.enums import AuditAction, LoanStatus, ScheduleStatus, TransactionType
from app.models.prepayment import Prepayment
from app.repositories import schedule_repository
from app.schemas.payment import PrepaymentOut, PrepaymentRequest
from app.services import account_service, audit_service, loan_service


def make_prepayment(
    db: Session, client: ClientProfile, user_id: int, loan_id: int, payload: PrepaymentRequest
) -> PrepaymentOut:
    loan = loan_service.get_client_loan_or_404(db, client.id, loan_id)
    if loan.status not in (LoanStatus.ACTIVE, LoanStatus.OVERDUE):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Loan is not active")

    amount = Decimal(payload.amount)
    outstanding = Decimal(loan.outstanding_principal)
    if amount > outstanding:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Prepayment exceeds outstanding principal")

    account = account_service.get_locked_account_for_client(db, client.id)
    transaction = account_service.debit(db, account, amount, TransactionType.PRINCIPAL_PREPAYMENT, "Loan", loan.id)

    prepayment = Prepayment(
        loan_id=loan.id,
        client_id=client.id,
        account_transaction_id=transaction.id,
        amount=amount,
        principal_reduction=amount,
    )
    db.add(prepayment)
    db.flush()

    new_outstanding = outstanding - amount
    loan.outstanding_principal = new_outstanding

    # The prepayment reduces outstanding principal immediately, but the effect on
    # EMI/interest is reflected only from the next due date - already-PAID
    # installments here are excluded and never modified.
    remaining_rows = schedule_repository.list_pending_or_overdue(db, loan.id)
    if remaining_rows:
        if new_outstanding <= 0:
            for row in remaining_rows:
                row.scheduled_principal = Decimal("0.00")
                row.scheduled_interest = Decimal("0.00")
                row.scheduled_amount = Decimal("0.00")
                row.remaining_principal = Decimal("0.00")
                row.status = ScheduleStatus.PAID
        else:
            due_dates = [row.due_date for row in remaining_rows]
            new_rows = recompute_schedule(
                new_outstanding,
                Decimal(loan.interest_rate),
                loan.repayment_frequency,
                due_dates,
                remaining_rows[0].installment_number,
            )
            for row, recomputed in zip(remaining_rows, new_rows):
                row.opening_principal = recomputed.opening_principal
                row.scheduled_principal = recomputed.principal_component
                row.scheduled_interest = recomputed.interest_component
                row.scheduled_amount = recomputed.installment_amount
                row.remaining_principal = recomputed.closing_principal

    audit_service.record(
        db,
        user_id=user_id,
        action=AuditAction.PRINCIPAL_PREPAYMENT,
        entity_type="Prepayment",
        entity_id=prepayment.id,
        new_value={"amount": amount, "new_outstanding_principal": new_outstanding},
    )

    loan_service.refresh_loan_status_after_payment(db, loan, user_id)

    db.commit()
    db.refresh(prepayment)
    return PrepaymentOut.model_validate(prepayment)
