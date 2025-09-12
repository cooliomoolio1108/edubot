from database import message_collection
from . import serialize_id, receive_one
from datetime import datetime

window = 8

def submit_chat_message(message_data):
    print("Message Data:", message_data)
    result = receive_one(message_collection, message_data)
    return result

def get_chat_message():
    message_list = list(message_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id
    return message_list

def get_chat_message_by_convoid(convo_id):
    messages = list(message_collection.find(
        {"conversation_id": convo_id}
    ).sort("timestamp", -1)
    .limit(window))
    results = list(reversed(messages))
    safe_messages = [serialize_id(m) for m in results]
    return safe_messages

def delete_message(convo_id):
    try:
        deleted_messages = message_collection.delete_many({
            "conversation_id": convo_id
        })
        if deleted_messages.deleted_count == 0:
            return "no messages deleted"
        
        return "deleted"
    except Exception as e:
        print(f"Error deleting messages for {convo_id}: {e}")
        return False