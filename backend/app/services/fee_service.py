from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.calculations.repayment import generate_schedule
from app.models.client_profile import ClientProfile
from app.models.enums import AuditAction, FeeStatus, LoanStatus, TransactionType
from app.models.repayment_schedule import RepaymentSchedule
from app.repositories import loan_repository, schedule_repository
from app.schemas.loan import LoanOut
from app.services import account_service, audit_service, loan_service


def pay_approval_fee(db: Session, client: ClientProfile, loan_id: int) -> LoanOut:
    loan = loan_service.get_client_loan_or_404(db, client.id, loan_id)
    if loan.status != LoanStatus.PENDING_FEE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Loan is not awaiting fee payment")

    fee = loan.fee
    if fee is None or fee.status != FeeStatus.PENDING:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Approval fee already paid")

    account = account_service.get_locked_account_for_client(db, client.id)
    now = datetime.now(timezone.utc)

    account_service.debit(
        db, account, fee.fee_amount, TransactionType.APPROVAL_FEE_PAYMENT, "LoanFee", fee.id
    )
    fee.status = FeeStatus.PAID
    fee.paid_at = now
    audit_service.record(
        db,
        user_id=client.user_id,
        action=AuditAction.APPROVAL_FEE_PAID,
        entity_type="LoanFee",
        entity_id=fee.id,
        new_value={"fee_amount": fee.fee_amount},
    )

    disbursement_txn = account_service.credit(
        db, account, loan.approved_amount, TransactionType.LOAN_DISBURSEMENT, "Loan", loan.id
    )
    audit_service.record(
        db,
        user_id=client.user_id,
        action=AuditAction.LOAN_DISBURSED,
        entity_type="Loan",
        entity_id=loan.id,
        new_value={"amount": loan.approved_amount, "account_transaction_id": disbursement_txn.id},
    )

    today = date.today()
    rows = generate_schedule(
        loan.approved_amount, loan.interest_rate, loan.duration_months, loan.repayment_frequency, today
    )
    schedule_rows = [
        RepaymentSchedule(
            loan_id=loan.id,
            installment_number=row.installment_number,
            due_date=row.due_date,
            opening_principal=row.opening_principal,
            scheduled_principal=row.principal_component,
            scheduled_interest=row.interest_component,
            scheduled_amount=row.installment_amount,
            remaining_principal=row.closing_principal,
        )
        for row in rows
    ]
    schedule_repository.create_many(db, schedule_rows)

    loan.start_date = today
    loan.end_date = rows[-1].due_date if rows else today
    loan.status = LoanStatus.ACTIVE
    audit_service.record(
        db, user_id=client.user_id, action=AuditAction.LOAN_ACTIVATED, entity_type="Loan", entity_id=loan.id
    )

    db.commit()
    return loan_service.to_loan_out(loan_repository.get_by_id(db, loan.id))
