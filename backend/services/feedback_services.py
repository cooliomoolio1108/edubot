from database import feedback_collection
from . import serialize_id

def get_feedback():
    feedbacks = feedback_collection.find()
    return [serialize_id(f) for f in feedbacks]

def get_feedback_details():
    feedback_details = list(feedback_collection.find({}, {"_id": 0}))
    return feedback_details

def submit_feedback(data):
    result = feedback_collection.insert_one(data)
    return result