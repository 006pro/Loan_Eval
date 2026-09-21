from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.enums import LoanStatus
from app.schemas.loan import LoanOut, RepaymentScheduleOut
from app.services import loan_service

router = APIRouter(prefix="/admin/loans", tags=["admin-loans"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[LoanOut])
def list_loans(
    loan_status: LoanStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[LoanOut]:
    return loan_service.list_all_loans(db, status_filter=loan_status)


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int, db: Session = Depends(get_db)) -> LoanOut:
    loan = loan_service.get_loan_assessed(db, loan_id)
    return loan_service.to_loan_out(loan)


@router.get("/{loan_id}/schedule", response_model=list[RepaymentScheduleOut])
def get_schedule(loan_id: int, db: Session = Depends(get_db)) -> list[RepaymentScheduleOut]:
    return loan_service.get_schedule_for_loan(db, loan_id)
