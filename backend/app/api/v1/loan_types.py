from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.master import LoanTypeOut
from app.services import master_service

router = APIRouter(prefix="/loan-types", tags=["loan-types"])


@router.get("", response_model=list[LoanTypeOut])
def list_active_loan_types(db: Session = Depends(get_db)) -> list[LoanTypeOut]:
    return master_service.list_loan_types(db, active_only=True)


@router.get("/{loan_type_id}", response_model=LoanTypeOut)
def get_loan_type(loan_type_id: int, db: Session = Depends(get_db)) -> LoanTypeOut:
    loan_type = master_service.get_loan_type_or_404(db, loan_type_id)
    return LoanTypeOut.model_validate(loan_type)
