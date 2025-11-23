from flask import Blueprint, jsonify, request
from services.feedback_services import get_feedback, submit_feedback
from utils.validators import success_response, fail_response, error_response
from utils.auth_check import require_auth
from services import get_user_id

feedback_routes = Blueprint("feedback", __name__)

@feedback_routes.route("/feedback", methods=["GET"])
@require_auth
def fetch_feedback():
    user_id = get_user_id()
    try:
        feedbacks = get_feedback(user_id)
        if feedbacks:
            return success_response(feedbacks)
        return fail_response("No feedback found")
    except Exception as e:
        error_response(e)

@feedback_routes.route("/feedback", methods=["POST"])
@require_auth
def receive_feedback():
    user_id = get_user_id()
    data = request.json
    reformatted_data = {
        "subject": data.get("subject", ""),
        "rating": data.get("rating", 3),
        "comment": data.get("comment", ""),
        "conversation_id": data.get("conversation_id", ""),
        "created_by": user_id
    }
    feedback_id = submit_feedback(reformatted_data)
    if feedback_id.inserted_id:
        return success_response(feedback_id.inserted_id, 201)
    return fail_response("Failed to submit feedback", 500)