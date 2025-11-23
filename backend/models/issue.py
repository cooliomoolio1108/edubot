from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Issue(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str = Field(..., min_length=1, max_length=100)
    desc: str = Field(..., min_length=1, max_length=200)
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    cat: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    reply: Optional[str] = Field(None, min_length=1, max_length=200)
    reply_by: Optional[str] = None