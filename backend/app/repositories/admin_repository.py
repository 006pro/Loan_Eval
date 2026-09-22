from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.admin_profile import AdminProfile


def get_by_user_id(db: Session, user_id: int) -> AdminProfile | None:
    return db.execute(select(AdminProfile).where(AdminProfile.user_id == user_id)).scalar_one_or_none()


def get_by_employee_id(db: Session, employee_id: str) -> AdminProfile | None:
    return db.execute(select(AdminProfile).where(AdminProfile.employee_id == employee_id)).scalar_one_or_none()


def list_all(db: Session) -> list[AdminProfile]:
    return list(
        db.execute(select(AdminProfile).options(joinedload(AdminProfile.user)).order_by(AdminProfile.id))
        .scalars()
        .all()
    )
