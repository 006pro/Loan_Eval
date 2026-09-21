from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_client
from app.models.user import User
from app.schemas.client import ClientProfileOut, ClientProfileUpdate
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(require_client)])


@router.get("/me", response_model=ClientProfileOut)
def get_my_profile(db: Session = Depends(get_db), user: User = Depends(require_client)) -> ClientProfileOut:
    return client_service.get_my_profile(db, user)


@router.put("/me", response_model=ClientProfileOut)
def update_my_profile(
    payload: ClientProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_client),
) -> ClientProfileOut:
    return client_service.update_my_profile(db, user, payload)
