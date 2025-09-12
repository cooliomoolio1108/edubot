from flask import Blueprint, jsonify, request
from services.course_services import find_course_details, find_courses
from models.course import Course
from pydantic import ValidationError
from utils.validators import success_response, fail_response, error_response

course_routes = Blueprint("courses", __name__)

@course_routes.route("/courses", methods=["GET"], strict_slashes=False)
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