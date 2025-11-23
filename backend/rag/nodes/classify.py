from . import llm_stream, embed_model, vector_store, RELEVANCE_THRESHOLD
from langchain_core.prompts import ChatPromptTemplate
from rag.graph.state import State
from spellchecker import SpellChecker

relevance_prompt = ChatPromptTemplate.from_template("""
You are a relevance classifier for an educational chatbot.
Decide whether this query is relevant to the course (RELEVANT) or not (IRRELEVANT).
If user says "hello" or initiates with a greeting, classify as RELEVANT.
This course is about {course_title}.""")

intent_prompt = ChatPromptTemplate.from_template("""
You are an intent classifier for an educational chatbot. 
Decide whether this query requires conceptual guidance (HINT) or factual information (DIRECT).
If user says "hello" or initiates with a greeting, classify as DIRECT.                                                  
If query is admin-based, it is DIRECT
                                                  
Query: {query}

Answer with one word only: "HINT" or "DIRECT".
""")

def classify_intent(state: State) -> State:
    if not state.get("main_query"):
        main_emd = embed_model.embed_query(state["query"])
        state["main_query"] = state["query"]
        state["main_emb"] = main_emd
        state["hint_stage"] = 0
    chain = intent_prompt | llm_stream
    resp = chain.invoke({"query": state["query"]}).content.strip().upper()
    print('This is the response from intent classifier:', resp)
    mode = "hint" if "HINT" in resp else "direct"
    print("THIS IS THE MODE", mode)
    return {**state, "mode": mode}

def classify_relevance(state: State) -> State:
    query = state.get("query", "")
    query = query.lower().strip()
    if not query:
        return {**state, "is_relevant": False, "relevance_score": 0.0}
    
    q_emb = embed_model.embed_query(query)
    q_results = vector_store.similarity_search_by_vector_with_relevance_scores(
        q_emb,
        k=1)
    if not q_results or not q_results[0]:
        return {**state, "is_relevant": False, "relevance_score": 0.0}
    top_doc, top_score = q_results[0]
    is_relevant = top_score < RELEVANCE_THRESHOLD
    return {**state, "is_relevant": is_relevant, "relevance_score": top_score}

def query_preprocess(state: State) -> State:
    state = classify_relevance(state)
    if not state.get("is_relevant", False):
        return state
    state = classify_intent(state)
    return state