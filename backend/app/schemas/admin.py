from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=150)
    employee_id: str = Field(min_length=1, max_length=30)


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    employee_id: str
    created_at: datetime
