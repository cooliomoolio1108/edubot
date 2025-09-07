from rag.graph.state import State
from rag.services.chroma_service import vector_store

def retrieve(state: State):
    print("Retrieving...")

    docs = vector_store.similarity_search(
        state["question"],
        k=3,
        filter={"course_id": state["course_id"]}
    )

    for i, d in enumerate(docs, 1):
        print(f"[{i}] Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')}")

    # Text form for the LLM
    context_text = "\n\n".join(
        f"{d.page_content}\n(Source: {d.metadata.get('source')}, Page: {d.metadata.get('page')})"
        for d in docs
    )

    # Keep the raw docs too, so later nodes (e.g., generate) can access metadata easily
    sources = [
        {
            "source": d.metadata.get("source"),
            "page": d.metadata.get("page"),
            "doc_id": d.metadata.get("doc_id"),
        }
        for d in docs
    ]
    test = {
        "context": context_text,   # for prompt
        "sources": sources,        # minimal metadata list
    }
    print("Retrieved: ", test)
    return test
