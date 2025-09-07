from flask import Blueprint, jsonify, request
from database.feedback_crud import get_feedback, submit_feedback

feedback_routes = Blueprint("feedback", __name__)

@feedback_routes.route("/feedback", methods=["GET"])
def fetch_feedback():
    feedback = get_feedback()
    return jsonify(feedback)

@feedback_routes.route("/feedback", methods=["POST"])
def receive_feedback():
    data = request.json
    feedback_id = submit_feedback(data)
    return jsonify({"message": "Feedback submitted", "feedback_id": str(feedback_id)}), 201