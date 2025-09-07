#cleaned
from . import course_collection
from . import serialize_id
from bson import ObjectId
from bson.errors import InvalidId
from typing import List, Type
from pydantic import BaseModel
from models.course import Course

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
