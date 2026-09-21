from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_client
from app.models.user import User
from app.schemas.loan_application import LoanApplicationOut, LoanApplicationPreviewOut, LoanApplicationRequest
from app.schemas.master import ApplicationConfigOut
from app.services import client_service, loan_application_service, master_service

router = APIRouter(prefix="/loan-applications", tags=["loan-applications"], dependencies=[Depends(require_client)])


@router.get("/config", response_model=ApplicationConfigOut)
def get_application_config(db: Session = Depends(get_db)) -> ApplicationConfigOut:
    return master_service.get_application_config(db)


@router.post("/preview", response_model=LoanApplicationPreviewOut)
def preview_application(
    payload: LoanApplicationRequest, db: Session = Depends(get_db)
) -> LoanApplicationPreviewOut:
    return loan_application_service.preview_application(db, payload)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LoanApplicationOut)
def submit_application(
    payload: LoanApplicationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_client),
) -> LoanApplicationOut:
    client = client_service.get_profile_or_404(db, user)
    return loan_application_service.submit_application(db, client, user.id, payload)


@router.get("", response_model=list[LoanApplicationOut])
def list_my_applications(
    db: Session = Depends(get_db), user: User = Depends(require_client)
) -> list[LoanApplicationOut]:
    client = client_service.get_profile_or_404(db, user)
    return loan_application_service.list_applications_for_client(db, client)


@router.get("/{application_id}", response_model=LoanApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_client),
) -> LoanApplicationOut:
    client = client_service.get_profile_or_404(db, user)
    return loan_application_service.get_application_for_client(db, client, application_id)
