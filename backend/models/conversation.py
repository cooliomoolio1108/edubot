from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Conversation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=2, max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    title_updated: bool = False
    course_id: str = Field(..., min_length=1, max_length=100)
    answer_mode: str = "direct"  # 0: direct, 1: classroom, 2: socratic, 3: quiz
    temperature: float = 0.2  # Default temperature for response generation
    main_query: Optional[str] = ""
    main_emb: Optional[list] = []
    hint_stage: Optional[int] = 0  # 0,1,2,
    response_speed: Optional[float] = 0  # 0: Normal, 1: Fast, 2: Slow
    response_tone: Optional[str] = "normal"  # 0: Normal, 1: Friendly, 2: Strict
    response_depth: Optional[str] = "normal"  # 0: Normal, 1: Shallow, 2: Deep

class UpdateConversation(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    user_id: Optional[str] = Field(None, min_length=2, max_length=100)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    title_updated: Optional[bool] = False
    course_id: Optional[str] = Field(None, min_length=1, max_length=100)
    answer_mode: Optional[str] = None
    temperature: Optional[float] = 0.2  # Default temperature for response generation
    main_query: Optional[str] = ""
    main_emb: Optional[list] = []
    hint_stage: Optional[int] = 0  # 0,1,2,
    response_speed: Optional[float] = 0  # 0: Normal, 1: Fast, 2: Slow
    response_tone: Optional[str] = "normal"  # 0: Normal, 1: Friendly, 2: Strict
    response_depth: Optional[str] = "normal"  # 0: Normal, 1: Shallow, 2: Deep