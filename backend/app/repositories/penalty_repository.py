from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.penalty import Penalty


def get_by_schedule_id(db: Session, schedule_id: int) -> Penalty | None:
    return db.execute(select(Penalty).where(Penalty.schedule_id == schedule_id)).scalar_one_or_none()


def create(db: Session, penalty: Penalty) -> Penalty:
    db.add(penalty)
    db.flush()
    return penalty
