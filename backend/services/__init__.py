from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import Type, Dict
from pydantic import BaseModel, ValidationError
from datetime import datetime
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from typing import List, Type
from flask import g
load_dotenv()

def get_user_id():
    user_id = g.current_user.get("_id")
    if user_id:
        return str(user_id)
    return None

def check_connection():
    try:
        client.server_info()  # Ping the server
        return {"status": "Success", "message": "Connected to MongoDB!"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}
    
def serialize_id(doc):
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    return doc

def clean_data(data: Dict, Model: Type[BaseModel]) -> Dict:
    """Validate a single dict against a Pydantic model."""
    try:
        validated = Model.model_validate(data)
        cleaned = validated.model_dump(by_alias=True, exclude_none=True)
        return cleaned
    except Exception as e:
        return {}

def receive_one(db_collection: Collection, data: dict, Model: Type[BaseModel]):
    try:
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        cleaned_data = clean_data(data, Model)

        result = db_collection.insert_one(cleaned_data)

        if result.acknowledged:
            return {
                "status": "success",
                "data": {"inserted_id": str(result.inserted_id)}
            }
        else:
            return {
                "status": "fail",
                "data": {"reason": "Insert not acknowledged"}
            }
    except PyMongoError as e:
        return {
            "status": "error",
            "message": "Database insert failed",
            "data": {"error": str(e)}
        }

