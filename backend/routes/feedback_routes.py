from flask import Blueprint, jsonify, request
from services.feedback_services import get_feedback, submit_feedback
from utils.validators import success_response, fail_response, error_response

feedback_routes = Blueprint("feedback", __name__)

@feedback_routes.route("/feedback", methods=["GET"])
def fetch_feedback():
    try:
        feedbacks = get_feedback()
        if feedbacks:
            return success_response(feedbacks)
        return fail_response("No feedback found")
    except Exception as e:
        error_response(e)

@feedback_routes.route("/feedback", methods=["POST"])
def receive_feedback():
    data = request.json
    feedback_id = submit_feedback(data)
    return jsonify({"message": "Feedback submitted", "feedback_id": str(feedback_id)}), 201