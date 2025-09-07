# routes/chat_routes.py
from flask import Blueprint, request, jsonify, Response, stream_with_context
from rag.services.openai_service import get_openai_response
from database.message_crud import get_chat_message_by_convoid, submit_chat_message
from database.prompt_crud import get_all_prompts, get_prompt
from rag.graph.graph import graph

chat_routes = Blueprint("chat", __name__)

@chat_routes.route("/chat", methods=["POST"])
def get_chat_response():
    data = request.get_json()
    convo_id, question, course_id, course_title = (
        data.get(k) for k in ("conversation_id", "prompt", "course_id", "course_title")
    )
    if not convo_id:
        return jsonify({"error": "Missing conversation ID"}), 400
    try:
        state = {
            "question": str(question),
            "convo_id": str(convo_id),
            "course_id": str(course_id),
            "course_title": str(course_title)
        }
        reply = graph.invoke(state)
        assistant_msg = {
            "role": "assistant",
            "content": reply.get("answer", ""),
            "conversation_id": convo_id,
            "sources": reply.get("sources", "")
        }
        submit_chat_message(assistant_msg)

        return jsonify({"answer": reply.get("answer", ''), "sources": reply.get("sources", [])})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@chat_routes.route("/prompt", methods=["GET"])
def get_prompts():
    try:
        response = get_all_prompts()
        if response:
            return jsonify(response)
        return jsonify({'error': 'No prompts found'}), 200
    except Exception as e:
        error_msg = str(e)
        return jsonify({'error':error_msg})
# @chat_routes.route("/prompt/<prompt_id>", methods=["GET"])
# def get_prompt(prompt_id):
