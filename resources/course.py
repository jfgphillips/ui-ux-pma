import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import courses
from schemas import CourseSchema, CourseUpdateSchema

blp = Blueprint("Courses", __name__, description="Operations on courses")


@blp.route("/courses")
class CourseList(MethodView):
    def get(self):
        return {"courses": list(courses.values())}

    @blp.arguments(CourseSchema)
    def post(self, course_data):
        for existing_courses in courses.values():
            if existing_courses["name"] == course_data["name"]:
                abort(400, message="Course already exists.")

        course_id = uuid.uuid4().hex
        course = {**course_data, "id": course_id}
        courses[course_id] = course
        return course, 201


@blp.route("/courses/<string:course_id>")
class Course(MethodView):
    def get(self, course_id):
        result = courses.get(course_id)
        if result:
            return result
        abort(404, message="Course not found.")

    def delete(self, course_id):
        result = courses.get(course_id)
        if result:
            del courses[course_id]
            return {"message": "student deleted"}
        abort(404, message="Student not found.")

    @blp.arguments(CourseUpdateSchema)
    def put(self, course_data, course_id):
        try:
            course = courses[course_id]
            course |= course_data
            return course
        except KeyError:
            abort(404, message="Course not found")
