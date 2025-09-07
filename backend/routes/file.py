import os
from flask import Blueprint, jsonify, request
from database.file_crud import find_files, find_files_by_course, save_files_to_db, find_file_by_id, embed_single_file, delete_file_by_id, delete_embed, find_embeds
from models.file import File
from utils.validators import success_response, fail_response, error_response
from pydantic import ValidationError
from database import clean_data
from datetime import datetime
from werkzeug.utils import secure_filename
from auth.auth_check import require_auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "backend", "documents")

file_routes = Blueprint("file", __name__)

@file_routes.route("/files", methods=["GET"])
def fetch_files():
    try:
        course_id = request.args.get("course_id")

        if course_id:
            data = find_files_by_course(course_id)
        else:
            data = find_files()

        if not data:
            return fail_response("No files found", 404)

        files = []
        if isinstance(data, list):
            for d in data:
                cleaned = clean_data(d, File)
                if cleaned:
                    files.append(cleaned)

        if not files:
            return fail_response("No valid files", 404)

        return success_response(files)

    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response(e)

@file_routes.route("/files", methods=["POST"])
def receive_file():
    uploaded = request.files.get("file")

    if not uploaded:
        return jsonify({"error": "No file part in request"}), 400
    print("Request Form:", request.form)
    metadata = {
        "course_id": request.form.get("course_id"),
        "uploaded_by": request.form.get("uploaded_by"),
        "title": request.form.get("title"),
        "file_size": request.form.get("file_size", ""),
        "uploaded_at": datetime.now(),
        "updated_at": datetime.now()
    }
    filename = secure_filename(uploaded.filename)

    folder_path = os.path.join(DOCUMENTS_DIR, request.form.get("course_id", "untagged"))
    os.makedirs(folder_path, exist_ok=True)
    save_path = os.path.join(folder_path, filename)
    uploaded.save(save_path)

    metadata["file_name"] = filename
    metadata["path"] = save_path
    metadata["embedded"] = False

    result = save_files_to_db(metadata)
    return jsonify({'result': result})

@file_routes.route("/files/<id>", methods=["DELETE"])
def delete_file(id):
    try:
        result = delete_file_by_id(id)
        if not result:
            return fail_response(f"{id} not found", 404)
        deleted = delete_embed(id)
        if not deleted:
            return fail_response("No files' vector store deleted", 404)
        return success_response(f"{id} deleted")
    except Exception as e:
        return error_response(e)

@file_routes.route("/files/embed", methods=["POST"])
@require_auth
def embed_file():
    try:
        file_id = request.json.get("file_id")
        if not file_id:
            return fail_response("No file_ids provided", 400)

        embedded_files = []
        failed_files = []
        file_doc = find_file_by_id(file_id)
        print(file_doc)
        if file_doc and not file_doc.get("embedded"):
            try:
                result = embed_single_file(file_doc)
                if result.get("status") == "embedded":
                    embedded_files.append({
                        "file_id": file_id,
                        "doc_count": result.get("doc_count", 0)
                    })
                else:
                    failed_files.append({
                        "file_id": file_id,
                        "reason": result.get("reason", "Unknown")
                    })
            except Exception as e:
                failed_files.append({
                    "file_id": file_id,
                    "reason": str(e)
                })
        else:
            failed_files.append({
                "file_id": file_id,
                "reason": "File not found or already embedded"
            })

        return success_response({
            "embedded_files": embedded_files,
            "failed_files": failed_files
        })

    except Exception as e:
        return error_response(e)

@file_routes.route("/files/embed", methods=["GET"])
def fetch_embeds():
    try:
        all_data = find_embeds()
        if not all_data["ids"]:
            return fail_response("Empty ChromaDB", 404)
        return success_response(all_data)
    except Exception as e:
        return error_response(e)