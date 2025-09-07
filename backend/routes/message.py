from flask import Blueprint, jsonify, request
from database.message_crud import get_chat_message, submit_chat_message, get_chat_message_by_convoid

message_routes = Blueprint("message", __name__)

@message_routes.route("/message", methods=["GET"])
def fetch_message():
    message = get_chat_message()
    return jsonify(message)


@message_routes.route("/message/<convo_id>", methods=["GET"])
def fetch_message_by_convoid(convo_id):
    messages = get_chat_message_by_convoid(convo_id)
    return jsonify([
        {
            "role": m["role"],
            "content": m["content"],
            "sources": m.get("sources")
        }
        for m in messages
    ])

from flask import request, jsonify
from werkzeug.exceptions import BadRequest, InternalServerError

@message_routes.route("/message", methods=["POST"])
def receive_message():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Missing JSON body.")
        
        required_fields = ["conversation_id", "role", "content"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise BadRequest(f"Missing required fields: {', '.join(missing)}")

        message_doc = submit_chat_message(data)

        return jsonify({
            "status": "success",
            "data": message_doc  # assuming this is JSON serializable
        }), 201

    except BadRequest as e:
        return jsonify({"status": "error", "error": str(e)}), 400
    
    except Exception as e:
        # Log the actual traceback here for debugging
        return jsonify({"status": "error", "error": "Internal server error"}), 500
