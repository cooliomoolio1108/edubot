from langchain_core.documents import Document
from typing_extensions import List, TypedDict, Dict
from typing import List, Optional

class State(TypedDict):
    is_relevant: Optional[bool]
    relevance_score: Optional[float]
    query: str
    main_query: Optional[str]
    main_emb: Optional[List[float]]
    hint_stage: Optional[int] #0,1,2,3 -> 3 is direct answer
    context: List[Document]
    answer: str
    course_title: str
    course_id: str
    convo_id: str
    history: List[Dict[str, str]]
    sources: List[Dict[str, str]]
    answer_mode: Optional[str]
    hint: Optional[str]
    response_tone: Optional[str]
    response_depth: Optional[str]
    response_speed: Optional[float]
    temperature: Optional[float]
    summary: Optional[str]
    is_classroom: bool
    classroom_dialogue: Optional[Dict]

class FeedbackState(TypedDict):
    feedback: List[dict]
    summary: str