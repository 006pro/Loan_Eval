from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas import master as schemas
from app.services import master_service

router = APIRouter(prefix="/admin/master", tags=["admin-master"], dependencies=[Depends(require_admin)])


@router.get("/duration", response_model=schemas.DurationRuleOut)
def get_duration_rule(db: Session = Depends(get_db)) -> schemas.DurationRuleOut:
    return master_service.get_duration_rule(db)


@router.put("/duration", response_model=schemas.DurationRuleOut)
def update_duration_rule(
    payload: schemas.DurationRuleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.DurationRuleOut:
    return master_service.update_duration_rule(db, admin.id, payload)


@router.get("/fees", response_model=schemas.ApprovalFeeRuleOut)
def get_fee_rule(db: Session = Depends(get_db)) -> schemas.ApprovalFeeRuleOut:
    return master_service.get_approval_fee_rule(db)


@router.put("/fees", response_model=schemas.ApprovalFeeRuleOut)
def update_fee_rule(
    payload: schemas.ApprovalFeeRuleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.ApprovalFeeRuleOut:
    return master_service.update_approval_fee_rule(db, admin.id, payload)


@router.get("/loan-types", response_model=list[schemas.LoanTypeOut])
def list_loan_types(db: Session = Depends(get_db)) -> list[schemas.LoanTypeOut]:
    return master_service.list_loan_types(db)


@router.post("/loan-types", status_code=status.HTTP_201_CREATED, response_model=schemas.LoanTypeOut)
def create_loan_type(
    payload: schemas.LoanTypeCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.LoanTypeOut:
    return master_service.create_loan_type(db, admin.id, payload)


@router.put("/loan-types/{loan_type_id}", response_model=schemas.LoanTypeOut)
def update_loan_type(
    loan_type_id: int,
    payload: schemas.LoanTypeUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.LoanTypeOut:
    return master_service.update_loan_type(db, admin.id, loan_type_id, payload)


@router.get("/repayment-frequencies", response_model=list[schemas.RepaymentFrequencyOut])
def list_repayment_frequencies(db: Session = Depends(get_db)) -> list[schemas.RepaymentFrequencyOut]:
    return master_service.list_repayment_frequencies(db)


@router.put("/repayment-frequencies/{frequency_id}", response_model=schemas.RepaymentFrequencyOut)
def update_repayment_frequency(
    frequency_id: int,
    payload: schemas.RepaymentFrequencyUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.RepaymentFrequencyOut:
    return master_service.update_repayment_frequency(db, admin.id, frequency_id, payload)


@router.get("/penalties", response_model=list[schemas.PenaltyRuleOut])
def list_penalty_rules(db: Session = Depends(get_db)) -> list[schemas.PenaltyRuleOut]:
    return master_service.list_penalty_rules(db)


@router.put("/penalties/{rule_id}", response_model=schemas.PenaltyRuleOut)
def update_penalty_rule(
    rule_id: int,
    payload: schemas.PenaltyRuleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> schemas.PenaltyRuleOut:
    return master_service.update_penalty_rule(db, admin.id, rule_id, payload)
