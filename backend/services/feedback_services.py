from database import feedback_collection
from models.feedback import Feedback
from . import serialize_id

def get_feedback(user_id):
    feedbacks = feedback_collection.find({"created_by": user_id})
    print(feedbacks)
    return [serialize_id(f) for f in feedbacks]

def get_feedback_details():
    feedback_details = list(feedback_collection.find({}, {"_id": 0}))
    return feedback_details

def submit_feedback(data):
    feedback = Feedback.model_validate(data)
    cleaned = feedback.model_dump(by_alias=True, exclude_none=True)
    result = feedback_collection.insert_one(cleaned)
    return result