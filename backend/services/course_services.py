#cleaned
from database import course_collection
from . import serialize_id
from bson import ObjectId
from bson.errors import InvalidId
from typing import List, Type
from pydantic import BaseModel, ValidationError
from models.course import Course, UpdateCourse

def find_courses() -> List[dict]:
    courses_cursor = course_collection.find()
    return [serialize_id(course) for course in courses_cursor]

def find_course_details(id: str) -> dict | None:
    try:
        oid = ObjectId(id)
    except InvalidId:
        return None  # invalid format
    doc = course_collection.find_one({"_id": oid})
    return serialize_id(doc) if doc else None

def submit_course(course_details: dict):
    def process(doc):
        return Course(**doc).dict(by_alias=True, exclude_none=True)
    try:
        cleaned = process(course_details)
        result = course_collection.insert_one(cleaned)
        if not result:
            return 0
        return str(result.inserted_id)
    except ValidationError as e:
        return e
    except Exception as e:
        return e

def delete_course_from_db(course_ids: List):
    try:
        object_ids = [ObjectId(cid) for cid in course_ids]
        result = course_collection.delete_many(
            {"_id":{"$in":object_ids}}
        )
        return result.deleted_count
    except Exception as e:
        return e

def edit_course_from_db(_id, edits):
    try:
        if isinstance(edits, dict) and _id:
            cleaned_edits = UpdateCourse(**edits)
            results = course_collection.update_one({"_id": ObjectId(_id)},{"$set":cleaned_edits})
            return results.modified_count
        return 0
    except Exception as e:
        return e