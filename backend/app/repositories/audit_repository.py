from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def list_recent(db: Session, *, limit: int = 200) -> list[AuditLog]:
    return list(db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).scalars())
