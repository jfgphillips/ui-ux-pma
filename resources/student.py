import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import students
from schemas import StudentSchema, StudentUpdateSchema

blp = Blueprint("Students", __name__, description="Operations on students")


@blp.route("/students")
class StudentList(MethodView):
    def get(self):
        return {"students": list(students.values())}

    @blp.arguments(StudentSchema)
    def post(self, student_data):
        for existing_student in students.values():
            if existing_student["email"] == student_data["email"]:
                abort(404, message="Student already exists.")

        student_id = uuid.uuid4().hex
        student = {**student_data, "id": student_id}
        students[student_id] = student

        return student, 201


@blp.route("/students/<string:student_id>")
class Student(MethodView):
    def get(self, student_id):
        result = students.get(student_id)
        if result:
            return result
        abort(404, message="Student not found.")

    def delete(self, student_id):
        result = students.get(student_id)
        if result:
            del students[student_id]
            return {"message": "student deleted"}
        abort(404, message="Student not found.")

    @blp.arguments(StudentUpdateSchema)
    def put(self, student_data, student_id):
        try:
            student = students[student_id]
            student |= student_data

            return student
        except KeyError:
            abort(404, "student not found")
