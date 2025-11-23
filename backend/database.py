from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv
from datetime import datetime

# Load .env variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)

# Use your DB
db = client["teaching_assistant"]

# Collections
feedback_collection = db["feedback"]
user_collection = db["user"]
conversation_collection = db["conversation"]
message_collection = db["message"]
chat_collection = db["chat"]
course_collection = db["course"]
file_collection = db["file"]
prompt_collection = db["prompt"]
req_category_collection = db["req_category"]
issue_collection = db["issue"]

# def seed_courses():
#     course = {
#         "course_name": "Multi-Disciplinary Project",
#         "course_code": "CS102",
#         "coordinator": "Prof. Benjamin Lee",
#         "sem": "1",
#         "created_at": datetime.fromisoformat("2025-08-25T09:00:00"),
#         "is_active": True,
#     }

#     existing = course_collection.find_one({"course_code": course["course_code"]})
#     if not existing:
#         course_collection.insert_one(course)
#         print(f"✅ Seeded course: {course['course_code']}")
#     else:
#         print(f"⚡ Course already exists: {existing['course_code']}")


def seed_users():
    user = {
        "oid": "caeb6f9c-03ba-4deb-bb50-950f1181adb3",
        "email": "gsim012@e.ntu.edu.sg",
        "name": "cooliomoolio11082000",
        "tenant_id": "15ce9348-be2a-462b-8fc0-e1765a9b204a",
        "role": "admin",
        "is_active": True,
        "created_at": datetime.fromisoformat("2025-09-02T16:55:00"),
        "last_login": datetime.fromisoformat("2025-09-09T16:21:31.611"),
        "updated_at": datetime.fromisoformat("2025-09-09T16:21:31.611"),
    }

    existing = user_collection.find_one({"oid": user["oid"]})
    if not existing:
        user_collection.insert_one(user)
        print(f"✅ Seeded admin user: {user['email']}")
    else:
        print(f"⚡ User already exists: {existing['email']}")

def ensure_indexes():
    # Courses → course_code should be unique
    course_collection.create_index([("course_code", ASCENDING)], unique=True)

    # Request categories → name should be unique
    req_category_collection.create_index([("name", ASCENDING)], unique=True)
    req_category_collection.create_index([("color", ASCENDING)], unique=True)

    # Issues → optional (title or combo constraints)
    issue_collection.create_index([("title", ASCENDING)], unique=False)
    print("✅ Indexes ensured")

# seed_courses()
seed_users()
ensure_indexes()
print("🎉 Database seeding complete")
print(course_collection.count_documents({}))
