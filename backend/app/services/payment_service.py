from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client_profile import ClientProfile
from app.models.enums import AuditAction, LoanStatus, PaymentType, PenaltyStatus, ScheduleStatus, TransactionType
from app.models.payment import Payment
from app.repositories import payment_repository, penalty_repository, schedule_repository
from app.schemas.payment import PaymentOut
from app.services import account_service, audit_service, loan_service, penalty_service


def pay_next_installment(db: Session, client: ClientProfile, user_id: int, loan_id: int) -> PaymentOut:
    loan = loan_service.get_client_loan_or_404(db, client.id, loan_id)
    if loan.status not in (LoanStatus.ACTIVE, LoanStatus.OVERDUE):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Loan is not active")

    penalty_service.assess_loan(db, loan)

    schedule = schedule_repository.get_next_payable(db, loan.id)
    if schedule is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Installment already paid")

    penalty = penalty_repository.get_by_schedule_id(db, schedule.id)
    penalty_due = Decimal(penalty.penalty_amount) if penalty is not None and penalty.status == PenaltyStatus.PENDING else Decimal("0.00")
    total_due = Decimal(schedule.scheduled_amount) + penalty_due

    account = account_service.get_locked_account_for_client(db, client.id)
    transaction = account_service.debit(
        db, account, total_due, TransactionType.EMI_PAYMENT, "RepaymentSchedule", schedule.id
    )

    payment = Payment(
        loan_id=loan.id,
        schedule_id=schedule.id,
        account_transaction_id=transaction.id,
        payment_type=PaymentType.EMI,
        amount=total_due,
        principal_amount=schedule.scheduled_principal,
        interest_amount=schedule.scheduled_interest,
        penalty_amount=penalty_due,
    )
    db.add(payment)
    db.flush()

    schedule.paid_principal = schedule.scheduled_principal
    schedule.paid_interest = schedule.scheduled_interest
    schedule.paid_amount = schedule.scheduled_amount
    schedule.status = ScheduleStatus.PAID
    schedule.paid_at = datetime.now(timezone.utc)

    if penalty_due > 0 and penalty is not None:
        penalty.status = PenaltyStatus.PAID

    loan.outstanding_principal = max(
        Decimal("0.00"), Decimal(loan.outstanding_principal) - Decimal(schedule.scheduled_principal)
    )

    audit_service.record(
        db,
        user_id=user_id,
        action=AuditAction.EMI_PAYMENT,
        entity_type="Payment",
        entity_id=payment.id,
        new_value={"amount": total_due, "penalty_amount": penalty_due},
    )

    loan_service.refresh_loan_status_after_payment(db, loan, user_id)

    db.commit()
    db.refresh(payment)
    return PaymentOut.model_validate(payment)


def list_payments_for_loan(db: Session, client_id: int, loan_id: int) -> list[PaymentOut]:
    loan_service.get_client_loan_or_404(db, client_id, loan_id)
    return [PaymentOut.model_validate(payment) for payment in payment_repository.list_by_loan(db, loan_id)]
