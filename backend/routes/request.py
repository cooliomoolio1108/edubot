from flask import Blueprint, jsonify, request
from services.request_services import get_categories, delete_cats_from_db, create_cat, get_issues, validate_cat, create_issues
from utils.validators import success_response, fail_response, error_response
from utils.auth_check import require_auth
from datetime import datetime
from services import get_user_id

request_routes = Blueprint("request", __name__)

@request_routes.route("/request/category", methods=["GET"])
@require_auth
def fetch_categories():
    try:
        data = get_categories()
        if not data:
            return fail_response("No data found")
        return success_response(data)
    except Exception as e:
        return error_response(e)

@request_routes.route("/request/category", methods=["POST"])
@require_auth
def add_categories():
    try:
        cat_data = request.json
        reformatted = {
            "name": cat_data.get("name", ""),
            "desc": cat_data.get("desc", ""),
            "color": cat_data.get("color", ""),
            "created_by": "None",
            "created_at": datetime.now(),
            "is_active": True
        }
        result= create_cat(reformatted)
        if not result:
            return fail_response("Category not created")
        return success_response(result)
    except Exception as e:
        return fail_response(str(e))
    
@request_routes.route("/request/category", methods=["DELETE"])
@require_auth
def delete_categories():
    try:
        ids = request.json   # expecting a list of string IDs
        if not ids or not isinstance(ids, list):
            return fail_response("No IDs provided")

        results = delete_cats_from_db(ids)
        if results == 0:
            return fail_response("No categories deleted")

        return success_response({"deleted_count": results})
    except Exception as e:
        return fail_response(str(e))
    
@request_routes.route("/request/issue", methods=["GET"])
@require_auth
def fetch_issues():
    try:
        data = get_issues()
        if not data:
            return fail_response("No data found")
        return success_response(data)
    except Exception as e:
        return error_response(e)

@request_routes.route("/request/issue", methods=["POST"])
@require_auth
def add_issues():
    user_id = get_user_id()
    try:
        issue_data = request.json
        cat = issue_data.get("cat", "")
        if not validate_cat(cat):
            fail_response("Category does not exist")
        reformatted = {
            "title": issue_data.get("title", ""),
            "desc": issue_data.get("desc", ""),
            "created_by": user_id,
            "created_at": datetime.now(),
            "is_active": True,
            "cat": cat,
        }
        result= create_issues(reformatted)
        if not result:
            return fail_response("Issue not created")
        return success_response(result)
    except Exception as e:
        return fail_response(str(e))