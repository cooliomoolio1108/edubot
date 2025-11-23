from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Classroom(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    main_query: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=2, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)