from rag.graph.state import State
from . import vector_store, embed_model

def retrieve(state: State):
    main_emb = state.get("main_emb")
    if main_emb and len(main_emb) > 0:
        query_embedding = state["main_emb"]
    else:
        query_embedding = embed_model.embed_query(state["query"])
    docs = vector_store.similarity_search_by_vector(
        query_embedding,
        k=5,
        filter={"course_id": state["course_id"]}
    )

    for i, d in enumerate(docs, 1):
        print(f"[{i}] Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')}")

    context_text = "\n\n".join(
        f"{d.page_content}\n(Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')})"
        for d in docs
    )
    sources = [
        {
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "doc_id": d.metadata.get("doc_id"),
        }
        for d in docs
    ]
    chunks = {
        "context": context_text,   # for prompt
        "sources": sources,        # minimal metadata list
    }
    return chunks
