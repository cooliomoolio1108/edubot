from database import req_category_collection as rq, issue_collection as ic
from . import serialize_id, get_user_id
from bson import ObjectId
from models.request_category import RequestCategory
from models.issue import Issue

def validate_cat(cat_id):
    if not rq.find_one({"_id": ObjectId(cat_id)}):
        return False
    return True

def get_categories():
    categories = rq.find()
    return [serialize_id(c) for c in categories]

def edit_cats_from_db(ids: list[str]):
    object_ids = [ObjectId(i) for i in ids]
    result = rq.update_many(
        {"_id": {"$in": object_ids}},       # filter: any of these IDs
        {"$set": {"is_active": False}}      # update: set inactive
    )
    return result.modified_count

def delete_cats_from_db(ids: list[str]):
    object_ids = [ObjectId(i) for i in ids]
    result = rq.delete_many(
        {"_id": {"$in": object_ids}}
    )
    return result.deleted_count

def create_cat(cat_data):
    def process(doc):
        return RequestCategory(**doc).model_dump(by_alias=True, exclude_none=True)
    if isinstance(cat_data, list) and len(cat_data) >= 1:
        cleaned = [process(c) for c in cat_data]
        result = rq.insert_many(cleaned)
        return result.inserted_ids
    else:
        cleaned = process(cat_data)
        result = rq.insert_one(cleaned)
        return result.inserted_id

def get_issues():
    user_id = get_user_id()
    issues = ic.find({"created_by": user_id})
    return [serialize_id(i) for i in issues]

def create_issues(issue_data):
    def process(doc):
        return Issue(**doc).model_dump(by_alias=True, exclude_none=True)
    if isinstance(issue_data, list) and len(issue_data) >= 1:
        cleaned = [process(i) for i in issue_data]
        result = ic.insert_many(cleaned)
        return result.inserted_ids
    else:
        cleaned = process(issue_data)
        result = ic.insert_one(cleaned)
        return result.inserted_id