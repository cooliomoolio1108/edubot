from langchain_core.prompts import ChatPromptTemplate
from rag.graph.state import State
from . import llm_stream
from . import embed_model
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))


hint_prompt = ChatPromptTemplate.from_template("""
You are a teaching assistant who helps students think critically.
Using the following reference material, generate 1 short conceptual hint.
that guide the student toward the answer but do not reveal it directly.
If the student wants the answer straight away, give them the answer.
Do not reveal the answer together with the hints.

Context:
{context}

Question: {question}

Hints (concise, thought-provoking):
""")

summary_prompt = ChatPromptTemplate.from_template("""
You are a teaching assistant who helps students think critically.
Using the following reference material, provide a concise summary
that captures the key concepts relevant to the student's question.
Summarise within 10 sentences, if possible.

Context (clean and summarise this, remove possible metadata noise and include only relevant info):
{context}
                                                  
If the student wants the answer straight away, give them the answer.
Do not reveal the answer together with the summary.
""")

def classify_main_query(state: State):
    main_query = state.get("main_query")
    hint_stage = state.get("hint_stage", 0)
    query = state.get("query")
    main_emb = state.get("main_emb")

    if not main_query:
        return {
            "main_query": query,
            "main_emb": embed_model.embed_query(query),
            "hint_stage": 0,
            "mode": "socratic"
        }
    new_emb = embed_model.embed_query(query)
    sim = cosine_similarity(main_emb, new_emb)
    print(f"[classify_main_query] Similarity = {sim:.3f}")

    if sim < 0.75:
        print("🔄 New topic detected, resetting main_query")
        return {
            "main_query": query,
            "main_emb": new_emb,
            "hint_stage": 0,
            "mode": "socratic"
        }

    if hint_stage < 3:
        return {
            "mode": "socratic",
            "hint_stage": hint_stage + 1
        }
    else:
        return {
            "mode": "direct",
            "hint_stage": 3
        }

def summarise_context(state: State) -> dict:
    print("Summarising context...")
    context_value = state["context"]
    if isinstance(context_value, str):
        context_str = context_value
    else:
        context_str = "\n\n".join(
            f"{d.page_content}\n(Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')})"
            for d in context_value
        )
    chain = summary_prompt | llm_stream
    summary_text = chain.invoke({
        "context": context_str,
    }).content.strip()
    print("This is the summarised context:", summary_text)
    return {"summary": summary_text, "context": context_str}

def generate_hints(state: State) -> dict:
    summary_text = state.get("summary", "")
    print("Generating hints...")
    context_value = state["context"]
    if isinstance(context_value, str):
        context_str = context_value
    else:
        context_str = "\n\n".join(
            f"{d.page_content}\n(Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')})"
            for d in context_value
        )
    print("Context String:", context_str)
    print("Question:", state["query"])
    chain = hint_prompt | llm_stream
    hint_text = chain.invoke({
        "context": context_str,
        "question": state["query"]
    }).content.strip()
    print("This is the generated hint:", hint_text)
    return {"hint": hint_text, "context": context_str, "summary": summary_text, "hint_stage" : state["hint_stage"]+ 1}
