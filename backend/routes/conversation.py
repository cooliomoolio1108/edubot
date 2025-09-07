from flask import Blueprint, request, jsonify
from rag.services.openai_service import generate_title_for_chat, get_openai_response
from database.conversation_crud import submit_chat_message, get_chat_message, get_convos, edit_title, delete_convo
from database.message_crud import get_chat_message, get_chat_message_by_convoid, delete_message

conversation_routes = Blueprint("conversation", __name__)

@conversation_routes.route("/conversation", methods=["POST"])
def receive_conversation():
    data = request.get_json()
    convo_result = submit_chat_message(data)
    return jsonify({"message": "Convo submitted", "conversation_id": str(convo_result.inserted_id)}), 201

@conversation_routes.route("/conversation", methods=["GET"])
def get_conversation():
    chat_message = get_convos()
    return jsonify(chat_message)

@conversation_routes.route("/generate_title", methods=["POST"])
def generate_title():
    print("generatea")
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
def delete_conversation(convo_id):
    delete_messages = delete_message(convo_id)
    if delete_messages:
        response = delete_convo(convo_id)
        if response:
            return jsonify({'status': 'success'}), 200
        return  jsonify({'error': 'Conversation not deleted'}), 404
    return jsonify({'error': 'Messages and Conversation not deleted'}), 404