from . import feedback_collection

def get_feedback():
    feedback_list = list(feedback_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id
    return feedback_list

def get_feedback_details():
    feedback_details = list(feedback_collection.find({}, {"_id": 0}))
    return feedback_details

def submit_feedback(data):
    result = feedback_collection.insert_one(data)
    return result