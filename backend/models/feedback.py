from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime, timezone

class Feedback(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    created_by: str = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    subject: Optional[Annotated[str, Field(max_length=100)]] = None
    rating: Optional[Annotated[int, Field(ge=1, le=5)]] = None
    comment: Optional[Annotated[str, Field(max_length=200)]] = None
    conversation_id: Optional[str] = None