from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class File(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    file_name: str = Field(..., min_length=1, max_length=100)
    path: Optional[str] = Field(..., min_length=1, max_length=300)
    course_id: str = Field(..., min_length=1, max_length=100)
    
    uploaded_by: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    embedded: bool = False
    file_size: Optional[int] = Field(None, ge=0)
    file_hash: Optional[str] = Field(None, min_length=64, max_length=64)