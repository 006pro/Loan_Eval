from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.admin_profile import AdminProfile
from app.models.enums import AuditAction, UserRole
from app.models.user import User
from app.repositories import admin_repository, user_repository
from app.schemas.admin import AdminCreateRequest, AdminOut
from app.services import audit_service


def _to_out(profile: AdminProfile) -> AdminOut:
    return AdminOut(
        id=profile.user_id,
        email=profile.user.email,
        name=profile.name,
        employee_id=profile.employee_id,
        created_at=profile.created_at,
    )


def list_admins(db: Session) -> list[AdminOut]:
    return [_to_out(profile) for profile in admin_repository.list_all(db)]


def create_admin(db: Session, actor_admin_id: int, payload: AdminCreateRequest) -> AdminOut:
    if user_repository.get_by_email(db, payload.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")
    if admin_repository.get_by_employee_id(db, payload.employee_id) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Employee ID is already in use")

    user = User(email=payload.email, password_hash=hash_password(payload.password), role=UserRole.ADMIN)
    db.add(user)
    db.flush()

    profile = AdminProfile(user_id=user.id, employee_id=payload.employee_id, name=payload.name)
    db.add(profile)
    db.flush()

    audit_service.record(
        db,
        user_id=actor_admin_id,
        action=AuditAction.ADMIN_CREATED,
        entity_type="User",
        entity_id=user.id,
        new_value={"email": user.email, "employee_id": profile.employee_id, "name": profile.name},
    )
    db.commit()

    return _to_out(profile)
