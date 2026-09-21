from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_client
from app.models.user import User
from app.schemas.loan import LoanFeeOut, LoanOut, RepaymentScheduleOut
from app.schemas.payment import PaymentOut, PrepaymentOut, PrepaymentRequest
from app.services import client_service, fee_service, loan_service, payment_service, prepayment_service

router = APIRouter(prefix="/loans", tags=["loans"], dependencies=[Depends(require_client)])


@router.get("", response_model=list[LoanOut])
def list_my_loans(db: Session = Depends(get_db), user: User = Depends(require_client)) -> list[LoanOut]:
    client = client_service.get_profile_or_404(db, user)
    return loan_service.list_loans_for_client(db, client.id)


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)) -> LoanOut:
    client = client_service.get_profile_or_404(db, user)
    loan = loan_service.get_client_loan_assessed(db, client.id, loan_id)
    return loan_service.to_loan_out(loan)


@router.get("/{loan_id}/schedule", response_model=list[RepaymentScheduleOut])
def get_schedule(
    loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)
) -> list[RepaymentScheduleOut]:
    client = client_service.get_profile_or_404(db, user)
    return loan_service.get_schedule_for_client_loan(db, client.id, loan_id)


@router.get("/{loan_id}/fee", response_model=LoanFeeOut)
def get_fee(loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)) -> LoanFeeOut:
    client = client_service.get_profile_or_404(db, user)
    return loan_service.get_fee_for_client_loan(db, client.id, loan_id)


@router.post("/{loan_id}/fee/pay", response_model=LoanOut)
def pay_fee(loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)) -> LoanOut:
    client = client_service.get_profile_or_404(db, user)
    return fee_service.pay_approval_fee(db, client, loan_id)


@router.post("/{loan_id}/payment", status_code=status.HTTP_201_CREATED, response_model=PaymentOut)
def pay_installment(loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)) -> PaymentOut:
    client = client_service.get_profile_or_404(db, user)
    return payment_service.pay_next_installment(db, client, user.id, loan_id)


@router.get("/{loan_id}/payments", response_model=list[PaymentOut])
def list_payments(
    loan_id: int, db: Session = Depends(get_db), user: User = Depends(require_client)
) -> list[PaymentOut]:
    client = client_service.get_profile_or_404(db, user)
    return payment_service.list_payments_for_loan(db, client.id, loan_id)


@router.post("/{loan_id}/prepayment", status_code=status.HTTP_201_CREATED, response_model=PrepaymentOut)
def make_prepayment(
    loan_id: int,
    payload: PrepaymentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_client),
) -> PrepaymentOut:
    client = client_service.get_profile_or_404(db, user)
    return prepayment_service.make_prepayment(db, client, user.id, loan_id, payload)
