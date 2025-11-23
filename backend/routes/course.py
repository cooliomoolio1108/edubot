from flask import Blueprint, jsonify, request
from services.course_services import find_course_details, find_courses, submit_course, delete_course_from_db, edit_course_from_db
from models.course import Course
from pydantic import ValidationError
from utils.validators import success_response, fail_response, error_response
from utils.auth_check import require_auth

course_routes = Blueprint("courses", __name__)

@course_routes.route("/courses", methods=["GET"], strict_slashes=False)
@require_auth
def fetch_all_courses():
    try:
        data = find_courses()
        if not data:
            return fail_response({"No courses found"}, 404)

        courses = []
        valid_errors = []
        for c in data:
            try:
                courses.append(Course(**c).model_dump(by_alias=True))
            except ValidationError as e:
                print("Validation error for course:", e)
                continue

        return success_response(courses)

    except Exception as e:
        return error_response(e, 500)


@course_routes.route("/courses/<id>", methods=["GET"])
@require_auth
def fetch_one_course(id):
    try:
        data = find_course_details(id)  # should return a dict
        if not data:
            return fail_response({"Course not found"}, 404)

        course = Course(**data).model_dump(by_alias=True)
        return success_response(course)

    except ValidationError as e:
        return fail_response({"errors": e.errors()}, 400)
    except Exception as e:
        return error_response(e, 500)
    
@course_routes.route("/courses", methods=["POST"])
@require_auth
def receive_course():
    try:
        course_details = request.json
        if course_details == None:
            return fail_response("No details received")
        result = submit_course(course_details)
        if not result:
            return fail_response("Unsuccesful")
        return success_response(result)
    except Exception as e:
        return error_response(e)

@course_routes.route("/courses", methods=["DELETE"])
@require_auth
def delete_course():
    try:
        delete_list = request.json
        if not isinstance(delete_list, list):
            return fail_response("Send list of deletion in correct [List] format")
        result = delete_course_from_db(delete_list)
        if result:
            return success_response(F"{result} document(s) deleted")
        return fail_response("Document(s) not deleted")
    except Exception as e:
        return error_response(e)
    
@course_routes.route("/courses/<_id>", methods=["PUT"])
@require_auth
def edit_course(_id):
    try:
        edits = request.json
        result = edit_course_from_db(_id, edits)
        if result:
            return success_response(edits)
        return fail_response("No edits done")
    except Exception as e:
        return error_response("Editing attempt failed")