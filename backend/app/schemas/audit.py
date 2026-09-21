from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditAction


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: AuditAction
    entity_type: str
    entity_id: int | None
    old_value: str | None
    new_value: str | None
    created_at: datetime
