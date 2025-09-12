from database import user_collection
from . import serialize_id
from bson import ObjectId

def get_user(id):
    result = serialize_id(user_collection.find_one({"_id": ObjectId(id)}))
    return result

def get_user_by_oid(oid):
    result = serialize_id(user_collection.find_one({"oid": oid}))
    return result

def create_user(user_data):
    if isinstance(user_data, list) and len(user_data) >= 1:
        result = user_collection.insert_many(user_data)
        return result.inserted_ids
    else:
        result = user_collection.insert_one(user_data)
        return result.inserted_id
    
def get_users():
    users_cursor = user_collection.find()
    return [serialize_id(user) for user in users_cursor]

def delete_user_from_db(id):
    delete_result = user_collection.delete_one({"_id": ObjectId(id)})
    return delete_result.deleted_count

def edit_user_from_db(id, edits):
    edit_result = user_collection.update_one({'_id':ObjectId(id)}, {'$set':edits})
    return edit_result.modified_count