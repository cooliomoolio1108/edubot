# rag/nodes/load_history.py
from rag.graph.state import State
from database import message_collection

WINDOW = 8

def get_chat_message_by_convoid(convo_id):
    messages = list(message_collection.find(
        {"conversation_id": convo_id}
    ).sort("timestamp", -1)
    .limit(WINDOW))
    return list(reversed(messages))

def load_history(state: State) -> State:
    print("Loading History...")
    msgs = get_chat_message_by_convoid(state['convo_id'])
    history = [{"role": m["role"], "content": m["content"]} for m in msgs]
    # convo = conversations_col.find_one({"_id": ObjectId(state["chat_id"])}, {"summary": 1})
    # state["summary"] = (convo or {}).get("summary", "")
    print("history:",history)
    return {"history": history}
