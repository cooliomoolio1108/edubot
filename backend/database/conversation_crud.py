from . import conversation_collection
from bson import ObjectId

def submit_chat_message(message_data):
    result = conversation_collection.insert_one(message_data)
    return result

def get_chat_message():
    message_list = list(conversation_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id
    return message_list

def submit_new_convo(convo_data):
    result = conversation_collection.insert_one(convo_data)
    return result

def get_convos():
    result = list(conversation_collection.find())
    for r in result:
        r["_id"] = str(r["_id"])
        print("TEST", r)
    return result

def edit_title(convo_id, new_title):
    print("editing title")
    try:
        result = conversation_collection.update_one(
            {"_id": ObjectId(convo_id)},
            {"$set": {"title": new_title, "title_updated":True}}
        )
        if result.modified_count == 1:
            print(f"✅ Title updated for conversation {convo_id}")
            return True
        else:
            print(f"⚠️ No document updated. Maybe ID not found?")
            return False
    except Exception as e:
        print(f"❌ Error updating title: {e}")
        return False
    
def delete_convo(convo_id):
    try:
        result = conversation_collection.delete_one({
            "_id": ObjectId(str(convo_id))
        })
        if result.deleted_count:
            return True
        return False
    except Exception as e:
        print('Exception:', e)
        return False
