from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RequestCategory(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    desc: str = Field(..., min_length=1, max_length=100)
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    color: str
    is_active: bool = True

class UpdateRequestCategory(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = Field(..., min_length=1, max_length=100)
    desc: Optional[str] = Field(..., min_length=1, max_length=100)
    created_by: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: Optional[bool] = True
    color: str
    