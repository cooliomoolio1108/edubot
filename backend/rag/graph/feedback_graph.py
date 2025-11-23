# rag/feedback/graph.py
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from ..nodes.summarise_feedback import load_feedback, summarise_feedback

class FeedbackSummaryState(TypedDict, total=False):
    feedback: List[Dict[str, Any]]
    summary: str

builder = StateGraph(FeedbackSummaryState)
builder.add_node("load_feedback", load_feedback)
builder.add_node("summarise_feedback", summarise_feedback)

builder.add_edge(START, "load_feedback")
builder.add_edge("load_feedback", "summarise_feedback")
builder.add_edge("summarise_feedback", END)

feedback_graph = builder.compile()
