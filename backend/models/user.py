from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime, timezone

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    oid: Optional[str] = ""
    name: Optional[str] = ""
    email: EmailStr
    role: Literal["admin", "staff", "student"] = "student"
    tenant_id: Optional[str] = ""      # Microsoft Entra tenant ID
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = datetime.utcnow()
    updated_at: Optional[datetime] = datetime.utcnow()

    class Config:
        populate_by_name = True
        orm_mode = True
