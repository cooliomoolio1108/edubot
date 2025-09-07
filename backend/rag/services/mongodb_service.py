from pymongo import MongoClient
import os
from dotenv import load_dotenv
from typing import List, Type
from pydantic import BaseModel

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