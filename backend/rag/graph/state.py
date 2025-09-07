from langchain_core.documents import Document
from typing_extensions import List, TypedDict, Dict

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    course_title: str
    course_id: str
    convo_id: str
    history: List[Dict[str, str]]
    sources: List[Dict[str, str]]