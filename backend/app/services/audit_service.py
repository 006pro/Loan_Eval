import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enums import AuditAction
from app.repositories import audit_repository
from app.schemas.audit import AuditLogOut


def record(
    db: Session,
    *,
    user_id: int | None,
    action: AuditAction,
    entity_type: str,
    entity_id: int | None = None,
    old_value: dict[str, Any] | None = None,
    new_value: dict[str, Any] | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=json.dumps(old_value, default=str) if old_value is not None else None,
        new_value=json.dumps(new_value, default=str) if new_value is not None else None,
    )
    db.add(log)
    db.flush()
    return log


def list_recent(db: Session, *, limit: int = 200) -> list[AuditLogOut]:
    return [AuditLogOut.model_validate(log) for log in audit_repository.list_recent(db, limit=limit)]
