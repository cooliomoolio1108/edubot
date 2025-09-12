import os
from flask import Blueprint, jsonify, request
from services.file_services import find_files, find_files_by_course, save_files_to_db, find_file_by_id, embed_single_file, delete_file_by_id, delete_embed, find_embeds
from services.gcp_services import open_pdf_from_gcp_stream, upload_file_to_gcp
from models.file import File
from utils.validators import success_response, fail_response, error_response
from pydantic import ValidationError
from services import clean_data
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.auth_check import require_auth
from utils.validators import success_response, fail_response, error_response
from services.embed_services import embed_pdf_bytes

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
    course_id = request.form.get("course_id", "uncategorized")
    gcp_path = f"courses/{course_id}/{uploaded.filename}"
    url = upload_file_to_gcp(uploaded, gcp_path)
    # folder_path = os.path.join(DOCUMENTS_DIR, request.form.get("course_id", "untagged"))
    # os.makedirs(folder_path, exist_ok=True)
    # save_path = os.path.join(folder_path, filename)
    # uploaded.save(save_path)
    if not url:
        return error_response("File(s) not uploaded")
    metadata["file_name"] = filename
    # metadata["path"] = save_path
    metadata["path"] = gcp_path
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
        _id = request.json.get("_id")
        if not _id:
            return fail_response("No file_id provided", 400)

        file_doc = find_file_by_id(_id)
        if not file_doc:
            return fail_response("File not found", 404)

        if file_doc.get("embedded", False):
            return fail_response("File is already embedded", 400)

        doc = open_pdf_from_gcp_stream(file_doc.get("path", False))
        result = embed_pdf_bytes(doc, file_doc)
        if result.get("status") == "embedded":
            return success_response(f"Embed success: {result.get('doc_count')} chunks embedded")
        else:
            return fail_response(f"Embed failed: {result.get('reason', 'Unknown reason')}", 500)

    except Exception as e:
        # Catch unexpected errors
        return error_response(f"Embed error: {str(e)}", 500)


@file_routes.route("/files/embed", methods=["GET"])
def fetch_embeds():
    try:
        all_data = find_embeds()
        if not all_data["ids"]:
            return fail_response("Empty ChromaDB", 404)
        return success_response(all_data)
    except Exception as e:
        return error_response(e)