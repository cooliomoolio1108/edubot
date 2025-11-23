from langgraph.graph import START, StateGraph, END
from rag.graph.state import State

# Import all your nodes
from rag.nodes.classify import classify_relevance
from rag.nodes.load_history import load_history
from rag.nodes.retrieve import retrieve
from rag.nodes.generate import generate, generate_classroom, generate_quiz
from rag.nodes.generate_hints import generate_hints, summarise_context, classify_main_query


# --- CONDITIONAL ROUTERS ---
def mode_branch(state: State):
    if state.get("is_classroom"):
        return "classroom"
    answer_mode = state.get("answer_mode", "direct")
    print("The mode is:", answer_mode)
    if answer_mode == "socratic":
        return "socratic"
    if answer_mode == "quiz":
        return "quiz"
    return "direct"

def build_graph():
    graph_builder = StateGraph(State)

    # Nodes
    graph_builder.add_node("classify_relevance", classify_relevance)
    graph_builder.add_node("load_history", load_history)
    graph_builder.add_node("retrieve", retrieve)
    graph_builder.add_node("generate", generate)
    graph_builder.add_node("classify_main_query", classify_main_query)
    graph_builder.add_node("summarise_context", summarise_context)
    graph_builder.add_node("generate_hints", generate_hints)
    graph_builder.add_node("generate_classroom", generate_classroom)
    graph_builder.add_node("generate_quiz", generate_quiz)

    # Base flow
    graph_builder.add_edge(START, "classify_relevance")
    graph_builder.add_conditional_edges(
        "classify_relevance",
        lambda x: True if x.get("is_relevant", False) else False,
        {True: "load_history", False: END}
    )
    graph_builder.add_edge("load_history", "retrieve")

    # Conditional routing after retrieval
    graph_builder.add_conditional_edges(
        "retrieve",
        mode_branch,
        {
            "direct": "generate",
            "socratic": "classify_main_query",
            "classroom": "generate_classroom",
            "quiz": "generate_quiz"
        }
    )

    # Hint flow
    graph_builder.add_conditional_edges(
        "classify_main_query",
        lambda s: s.get("mode", "socratic"),
        {
            "socratic": "summarise_context",
            "direct": "generate"
        }
                                        )
    graph_builder.add_edge("summarise_context", "generate_hints")
    graph_builder.add_edge(
        "generate_hints",
        END
    )

    # Final endpoints
    graph_builder.add_edge("generate_classroom", END)
    graph_builder.add_edge("generate_quiz", END)
    graph_builder.add_edge("generate", END)
    
    return graph_builder.compile()

graph = build_graph()
