from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.client_profile import ClientProfile
from app.models.enums import AuditAction, UserRole
from app.models.user import User
from app.repositories import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services import account_service, audit_service


def register_client(db: Session, data: RegisterRequest) -> TokenResponse:
    if user_repository.get_by_email(db, data.email) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")

    user = User(email=data.email, password_hash=hash_password(data.password), role=UserRole.CLIENT)
    db.add(user)
    db.flush()

    client = ClientProfile(user_id=user.id, name=data.name, phone=data.phone)
    db.add(client)
    db.flush()

    account_service.create_virtual_account(db, client)
    db.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(access_token=token, role=user.role)


def authenticate(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_repository.get_by_email(db, data.email)
    if user is None or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    audit_service.record(
        db, user_id=user.id, action=AuditAction.LOGIN, entity_type="User", entity_id=user.id
    )
    db.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(access_token=token, role=user.role)
