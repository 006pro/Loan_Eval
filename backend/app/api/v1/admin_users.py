from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.models.user import User
from app.schemas.admin import AdminCreateRequest, AdminOut
from app.services import admin_service

router = APIRouter(prefix="/admin/admins", tags=["admin-users"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[AdminOut])
def list_admins(db: Session = Depends(get_db)) -> list[AdminOut]:
    return admin_service.list_admins(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AdminOut)
def create_admin(
    payload: AdminCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminOut:
    return admin_service.create_admin(db, admin.id, payload)
