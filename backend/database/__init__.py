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

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["teaching_assistant"]

feedback_collection = db["feedback"]
user_collection = db["user"]
conversation_collection =  db["conversation"]
message_collection = db["message"]
chat_collection = db['chat']
course_collection = db['course']
file_collection = db['file']
prompt_collection = db['prompt']

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
        return Model(**data).dict(by_alias=True)
    except Exception as e:
        return {}

def receive_one(db_collection: Collection, data: dict):
    try:
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        # cleaned_data = clean_data(data)

        result = db_collection.insert_one(data)

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

