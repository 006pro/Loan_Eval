from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin_profile import AdminProfile


def get_by_user_id(db: Session, user_id: int) -> AdminProfile | None:
    return db.execute(select(AdminProfile).where(AdminProfile.user_id == user_id)).scalar_one_or_none()
