from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin
from app.schemas.audit import AuditLogOut
from app.services import audit_service

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit-logs"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)
) -> list[AuditLogOut]:
    return audit_service.list_recent(db, limit=limit)
