import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import course_registers
from old_app import app
from schemas import CourseRegisterSchema, CourseRegisterUpdateSchema

blp = Blueprint("Course Registers", __name__, description="Operations on registers")


@blp.route("/course_registers")
class CourseRegisterList(MethodView):
    def get(self):
        return {"course list": list(course_registers.values())}

    @blp.arguments(CourseRegisterSchema)
    def post(self, course_register_data):

        for existing_course_register in course_registers:
            if existing_course_register["course_id"] == course_register_data["course_id"]:
                abort(400, message="Bad request, course already created in register")

        register_id = uuid.uuid4().hex
        course_register = {**course_register_data, "id": register_id}
        course_registers[register_id] = course_register
        return course_register, 201


@blp.route("/course_registers/<string:register_id>")
class CourseRegister(MethodView):
    def get(self, register_id):
        result = course_registers.get(register_id)
        if result:
            return result
        abort(404, message="Course not found.")

    @blp.arguments(CourseRegisterUpdateSchema)
    def put(self, payload, register_id):
        course_register = course_registers.get(register_id)
        if not course_register:
            abort(404, message="course does not exist")

        for student in payload["students"]:
            if student in course_register["students"]:
                app.logger.warning("student already enrolled skipping")
                continue

            course_register["students"].append(student)

        course_registers[register_id] = course_register

        return course_register, 204

    def delete(self, register_id):
        result = course_registers.get(register_id)
        if result:
            del course_registers[register_id]
            return {"message": "course register deleted"}
        abort(404, message="course register not found.")
