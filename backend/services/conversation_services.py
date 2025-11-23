from database import conversation_collection
from bson import ObjectId
from models.conversation import Conversation, UpdateConversation
from pydantic import ValidationError
from. import get_user_id, serialize_id

def insert_convo(convo_data):
    try:
        convo = Conversation.model_validate(convo_data)
        cleaned = convo.model_dump(by_alias=True, exclude_none=True)
        result = conversation_collection.insert_one(cleaned)
        return result
    except Exception as e:
        return e
    except ValidationError as e:
        return e

def get_chat_message():
    user_id = get_user_id()
    messages = list(
        conversation_collection.find(
            {"user_id": user_id},
        )
    )
    return messages

def submit_new_convo(convo_data):
    result = conversation_collection.insert_one(convo_data)
    return result

def get_convos():
    user_id = get_user_id()
    result = list(conversation_collection.find({"user_id": user_id}))
    for r in result:
        r["_id"] = str(r["_id"])
        print("TEST", r)
    return result

def edit_convo(convo_id, updated_data):
    try:
        if isinstance(updated_data, dict) and convo_id:
            cleaned_edits = UpdateConversation(**updated_data)
            cleaned_edits = cleaned_edits.model_dump(exclude_none=True, exclude_unset=True)
            print("CLEANED EDITS:", cleaned_edits)
            result = conversation_collection.update_one(
                {"_id": ObjectId(convo_id)},
                {"$set": cleaned_edits}
            )
            if result.modified_count == 1:
                return True
        else:
            return False
    except Exception as e:
        print(f"Error updating conversation: {e}")
        return False

def get_convo_by_id(convo_id):
    try:
        convo = conversation_collection.find_one({"_id": ObjectId(convo_id)})
        if convo:
            serialize_id(convo)
            return convo
        return None
    except Exception as e:
        print(f"Error retrieving conversation by ID: {e}")
        return None

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
