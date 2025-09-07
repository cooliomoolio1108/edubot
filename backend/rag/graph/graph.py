from langgraph.graph import START, StateGraph
from .state import State
from rag.nodes.generate import generate
from rag.nodes.retrieve import retrieve
from rag.nodes.load_history import load_history

graph_builder = StateGraph(State).add_sequence([load_history, retrieve, generate])
graph_builder.add_edge(START, "load_history")
graph_builder.add_edge("load_history", "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph = graph_builder.compile()