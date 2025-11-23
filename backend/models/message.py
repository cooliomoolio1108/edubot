from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class Message(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    role: str = Field(..., min_length=1, description="Role of sender (e.g., 'user', 'assistant')")
    content: str = Field(..., min_length=1, description="Message text or content")
    conversation_id: str = Field(..., min_length=1, description="Associated conversation ID")
    sources: Optional[List[Any]] = Field(default_factory=list, description="List of message sources")
    answer_mode: Optional[str] = Field(default="None", description="Message mode (e.g., 'hint', 'None')")
    summary: Optional[str] = Field(default="", description="Short summary of the context or answer")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_classroom: bool = Field(default=False, description="True if message is part of a classroom session")