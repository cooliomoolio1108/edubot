from flask import g, Blueprint, request, jsonify
from models.conversation import Conversation
from rag.services.openai_service import generate_title_for_chat, get_openai_response
from services.conversation_services import insert_convo, get_convos, edit_title, delete_convo, edit_convo
from services.message_services import get_chat_message_by_convoid, delete_message
from utils.auth_check import require_auth
from utils.validators import success_response, fail_response, error_response

conversation_routes = Blueprint("conversation", __name__)

@conversation_routes.route("/conversation", methods=["POST"])
@require_auth
def receive_conversation():
    data = request.get_json()
    user = g.current_user
    convo_data = {
        "title": data.get("title"),
        "user_id": user.get("_id"),
        "course_id": data.get("course_id"),
    }
    convo_result = insert_convo(convo_data)
    if not convo_result:
        return fail_response("fail")
    return success_response(convo_result.inserted_id)

@conversation_routes.route("/conversation", methods=["GET"])
@require_auth
def get_conversation():
    chat_message = get_convos()
    return jsonify(chat_message)

@conversation_routes.route("/generate_title", methods=["POST"])
@require_auth
def generate_title():
    data = request.get_json()
    convo_id = data.get("conversation_id")

    if not convo_id:
        return jsonify({"error": "Missing conversation_id"}), 400

    messages = get_chat_message_by_convoid(convo_id)

    try:
        new_title = generate_title_for_chat(messages)
        success = edit_title(convo_id, new_title)
        if success:
            return jsonify({"title": new_title}), 200
        else:
            return jsonify({"error": "Failed to update title"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@conversation_routes.route("/conversation/<convo_id>", methods=["DELETE"])
@require_auth
def delete_conversation(convo_id):
    delete_messages = delete_message(convo_id)
    if delete_messages:
        response = delete_convo(convo_id)
        if response:
            return jsonify({'status': 'success'}), 200
        return  jsonify({'error': 'Conversation not deleted'}), 404
    return jsonify({'error': 'Messages and Conversation not deleted'}), 404

@conversation_routes.route("/conversation/<convo_id>", methods=["PUT"])
@require_auth
def update_conversation(convo_id):
    data = request.get_json()
    if not data:
        return fail_response("No data provided", 400)
    success = edit_convo(convo_id, data)
    if success:
        return success_response("Conversation updated successfully")
    else:
        return fail_response("Failed to update conversation", 500)