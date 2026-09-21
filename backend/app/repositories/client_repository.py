from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client_profile import ClientProfile


def get_by_user_id(db: Session, user_id: int) -> ClientProfile | None:
    return db.execute(select(ClientProfile).where(ClientProfile.user_id == user_id)).scalar_one_or_none()


def get_by_id(db: Session, client_id: int) -> ClientProfile | None:
    return db.get(ClientProfile, client_id)
