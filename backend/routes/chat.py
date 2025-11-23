# routes/chat_routes.py
from flask import Blueprint, request, jsonify, Response, stream_with_context
from rag.services.openai_service import get_openai_response
from services.message_services import get_chat_message_by_convoid, submit_chat_message
from services.prompt_services import get_all_prompts, get_prompt
from services.conversation_services import get_convo_by_id, edit_convo
from rag.graph.graph import graph
from rag.graph.feedback_graph import feedback_graph
from utils.auth_check import require_auth
from utils.validators import success_response, fail_response, error_response
import json
from datetime import datetime

chat_routes = Blueprint("chat", __name__)

@chat_routes.route("/chat", methods=["POST"])
@require_auth
def get_chat_response():
    convo_tuple = ("main_query", "course_id", "hint_stage", "main_emb", "answer_mode", "temperature", "response_tone", "response_depth")
    data = request.get_json()
    convo_id, query, course_title, is_classroom = (
        data.get(k) for k in ("convo_id", "query", "course_title", "is_classroom")
    )
    if not convo_id:
        return jsonify({"error": "Missing conversation ID"}), 400
    convo_data = get_convo_by_id(convo_id)
    print(convo_data)
    if not convo_data:
        return jsonify({"error": "Conversation not found"}), 404
    main_query, course_id, hint_stage, main_emb, answer_mode, temperature, response_tone, response_depth = (
        convo_data.get(k) for k in convo_tuple
    )
    try:
        state = {
            "query": str(query),
            "main_query": str(main_query),
            "convo_id": str(convo_id),
            "course_id": str(course_id),
            "course_title": str(course_title),
            "hint_stage": hint_stage,
            "main_emb": main_emb if main_emb else None,
            "answer_mode": str(answer_mode),
            "temperature": float(temperature) if temperature is not None else 0.2,
            "response_tone": str(response_tone) if response_tone is not None else "normal",
            "response_depth": str(response_depth) if response_depth is not None else "normal",
            "is_classroom": bool(is_classroom)
        }
        print("State being sent to graph:", state)
        reply = graph.invoke(state)
        content = reply.get("answer", "")
        if not content:
            content = reply.get("hint", "I'm sorry, I couldn't generate a response.")
        assistant_msg = {
            "role": "assistant",
            "content": content,
            "conversation_id": convo_id,
            "sources": reply.get("sources", ""),
            "answer_mode": reply.get("answer_mode", ""),
            "summary": reply.get("summary", ""),
            "is_classroom": is_classroom
        }
        print(reply.get("classroom_dialogue"))
        result = submit_chat_message(assistant_msg)
        convo_edit = edit_convo(convo_id, {
            "main_query": reply.get("main_query", ""),
            "main_emb": reply.get("main_emb", []),
            "hint_stage": reply.get("hint_stage", 0),
            "updated_at": datetime.now()
        })
        data = result.get("data", "")
        if data:
            inserted_id = data.get("inserted_id", "")
        else:
            inserted_id = ""

        return jsonify({"content": content, "sources": reply.get("sources", []), "answer_mode": reply.get("answer_mode", ""), "inserted_id": str(inserted_id), "context": reply.get("context", ""), "summary":reply.get("summary", "")}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@chat_routes.route("/prompt", methods=["GET"])
@require_auth
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

@chat_routes.route("/feedback/ai", methods=["GET"])
def get_ai_feedback_summary():
    try:
        reply = feedback_graph.invoke({"feedback":[]})
        summary = reply.get("summary", "")
        return success_response(summary)
    except Exception as e:
        print(e)
        return error_response(e)

@chat_routes.route("/chat/classroom", methods=["POST"])
@require_auth
def get_chat_response_classroom():
    print("Received Message")

    convo_tuple = ("main_query", "course_id", "hint_stage", "main_emb", "answer_mode", "temperature", "response_tone", "response_depth")
    data = request.get_json()
    convo_id, query, course_title, is_classroom = (
        data.get(k) for k in ("convo_id", "query", "course_title", "is_classroom")
    )

    convo_data = get_convo_by_id(convo_id)
    if not convo_data:
        return jsonify({"error": "Conversation not found"}), 404

    main_query, course_id, hint_stage, main_emb, answer_mode, temperature, response_tone, response_depth = (
        convo_data.get(k) for k in convo_tuple
    )

    state = {
        "query": str(query),
        "main_query": str(main_query),
        "convo_id": str(convo_id),
        "course_id": str(course_id),
        "course_title": str(course_title),
        "hint_stage": hint_stage,
        "main_emb": main_emb if main_emb else None,
        "answer_mode": str(answer_mode),
        "temperature": float(temperature) if temperature is not None else 0.2,
        "response_tone": str(response_tone) if response_tone is not None else "normal",
        "response_depth": str(response_depth) if response_depth is not None else "normal",
        "is_classroom": bool(is_classroom)
    }

    print("State being sent to graph:", state)

    def generate():
        all_chunks = ""
        print("Streaming started", flush=True)
        for chunk in graph.stream(state, stream_mode="custom"):
            to_app = str(chunk) + "\n"
            all_chunks += to_app
            yield f"data: {json.dumps(chunk)}\n\n"
        print("Streaming complete", flush=True)
        assistant_msg = {
            "role": "assistant",
            "content": str(all_chunks),
            "conversation_id": convo_id,
            "sources": [],
            "answer_mode": answer_mode,
            "summary": "",
            "is_classroom": is_classroom
        }
        submit_chat_message(assistant_msg)
        yield "data: [END]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")