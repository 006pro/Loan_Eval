from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.client_profile import ClientProfile
from app.models.user import User
from app.repositories import client_repository
from app.schemas.client import ClientProfileOut, ClientProfileUpdate


def get_profile_or_404(db: Session, user: User) -> ClientProfile:
    profile = client_repository.get_by_user_id(db, user.id)
    if profile is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client profile not found")
    return profile


def _to_out(profile: ClientProfile) -> ClientProfileOut:
    return ClientProfileOut(
        id=profile.id,
        email=profile.user.email,
        name=profile.name,
        phone=profile.phone,
        address=profile.address,
        date_of_birth=profile.date_of_birth,
        employment=profile.employment,
        monthly_income=profile.monthly_income,
        yearly_income=profile.yearly_income,
        existing_loans=profile.existing_loans,
        bank_account_number=profile.bank_account_number,
        credit_score=profile.credit_score,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def get_my_profile(db: Session, user: User) -> ClientProfileOut:
    return _to_out(get_profile_or_404(db, user))


def update_my_profile(db: Session, user: User, payload: ClientProfileUpdate) -> ClientProfileOut:
    profile = get_profile_or_404(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return _to_out(profile)


def is_profile_complete(profile: ClientProfile) -> bool:
    return bool(profile.phone and profile.address and profile.monthly_income is not None)
