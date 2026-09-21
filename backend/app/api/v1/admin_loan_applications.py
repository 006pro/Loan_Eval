from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.enums import ApplicationStatus
from app.models.user import User
from app.schemas.evaluation import AdminLoanApplicationOut, ApprovalRequest, RejectionRequest
from app.schemas.loan import LoanOut
from app.services import evaluation_service

router = APIRouter(
    prefix="/admin/loan-applications", tags=["admin-loan-applications"], dependencies=[Depends(require_admin)]
)


@router.get("", response_model=list[AdminLoanApplicationOut])
def list_applications(
    application_status: ApplicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[AdminLoanApplicationOut]:
    return evaluation_service.list_applications(db, status_filter=application_status)


@router.get("/{application_id}", response_model=AdminLoanApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)) -> AdminLoanApplicationOut:
    return evaluation_service.get_application(db, application_id)


@router.post("/{application_id}/approve", response_model=LoanOut)
def approve_application(
    application_id: int,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> LoanOut:
    return evaluation_service.approve_application(db, admin.id, application_id, payload)


@router.post("/{application_id}/reject", response_model=AdminLoanApplicationOut)
def reject_application(
    application_id: int,
    payload: RejectionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminLoanApplicationOut:
    return evaluation_service.reject_application(db, admin.id, application_id, payload)
