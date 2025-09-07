from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Course(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    course_name: str = Field(..., min_length=1, max_length=100)
    course_code: str = Field(..., min_length=2, max_length=20)
    coordinator: str = Field(..., min_length=2, max_length=100)
    sem: str = Field(..., pattern=r"^(1|2|special)$", description="Semester name")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_active: bool = True