from flask import Blueprint, jsonify, request
from database.user_crud import get_user, create_user, get_users, delete_user_from_db, edit_user_from_db, get_user_by_oid
from models.user import User
from utils.validators import success_response, fail_response, error_response
from pydantic import ValidationError

user_routes = Blueprint("user", __name__)

@user_routes.route("/users/<id>", methods=["GET"])
def fetch_user(id):
    try:
        user_doc = get_user(id)
        if not user_doc:
            return fail_response({"reason": "User not found"}, 404)
        user = User(**user_doc)
        return success_response(user.dict(by_alias=True))
    except Exception as e:
        return error_response(e)
    except ValidationError as e:
        return error_response(e)
    
@user_routes.route("/users/oid/<oid>", methods=["GET"])
def fetch_user_by_oid(oid):
    try:
        user_doc = get_user_by_oid(oid)
        if not user_doc:
            return fail_response({"reason": "User not found"}, 404)
        user = User(**user_doc)
        return success_response(user.dict(by_alias=True))
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response(e)

@user_routes.route("/users", methods=["POST"])
def add_user():
    data = request.json
    try:
        if isinstance(data, dict):
            users = [User(**data).model_dump()]
        elif isinstance(data, list):
            users = [User(**u).model_dump() for u in data]
        else:
            return fail_response({"Invalid payload"}, 400)
    except ValidationError as e:
        return fail_response({"errors": e.errors()}, 400)

    try:
        user_ids = create_user(users)

        if not isinstance(user_ids, list):
            user_ids = [user_ids]

        return success_response({"user_ids": [str(i) for i in user_ids]}, 201)

    except Exception as e:
        return error_response(e, 500)

@user_routes.route("/users", methods=["GET"])
def fetch_all_users():
    try:
        data = get_users()
        if not data:
            return fail_response({"No users found"}, 404)

        users = []
        for u in data:
            try:
                users.append(User(**u).model_dump(by_alias=True))
            except Exception as e:
                print("Validation error for user:", e)
                continue

        return success_response(users)

    except Exception as e:
        return error_response(e, 500)

@user_routes.route("/users/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        result = delete_user_from_db(id)
        if not result:
            return fail_response({"id": id, "reason": "User not found"}, 404)
        return success_response({"deleted": id})
    except Exception as e:
        return error_response(e)

@user_routes.route("/users/<id>", methods=["PUT"])
def edit_user(id):
    data = request.json
    if not isinstance(data, dict) or not isinstance(data.get("edits"), dict):
        return fail_response("Invalid payload", 400)

    try:
        result = edit_user_from_db(id, data["edits"])
        if not result:
            return fail_response({"id": id, "reason": "User not found"}, 404)
        return success_response({"edited": id})
    except Exception as e:
        return error_response(e)