from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256

from db import db
from models import StudentModel
from schemas import StudentSchema, StudentUpdateSchema

blp = Blueprint("Students", __name__, description="Operations on students")


@blp.route("/students")
class StudentList(MethodView):
    @blp.response(200, StudentSchema(many=True))
    def get(self):
        return StudentModel.query.all()

    @blp.arguments(StudentSchema, location="form", content_type="form")
    @blp.response(201, StudentSchema)
    def post(self, student_data):
        if StudentModel.query.filter(StudentModel.username == student_data["username"]).first():
            abort(409, message="a student with that username already exists")

        student_data["password"] = pbkdf2_sha256.hash(student_data["password"])
        student = StudentModel(**student_data)

        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")

        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when adding student to db: {e}")

        return student


@blp.route("/students/<int:student_id>")
class Student(MethodView):
    @staticmethod
    @blp.response(200, StudentSchema)
    def get(student_id):
        student = StudentModel.query.get_or_404(student_id)
        return student

    @jwt_required()
    def delete(self, student_id):
        jwt_payload = get_jwt()
        if jwt_payload["user_type"] == "admin" or jwt_payload["sub"] == student_id:
            student = StudentModel.query.get_or_404(student_id)
            db.session.delete(student)
            db.session.commit()
            return {"message": "deleted student"}

        abort(401, message="you are not allowed to delete other accounts")

    @blp.arguments(StudentUpdateSchema)
    @blp.response(204, StudentSchema)
    def put(self, student_data, student_id):
        student = StudentModel.query.get(student_id)
        if student:
            for key, value in student_data.items():
                setattr(student, key, value)
            status_code = 200

        else:
            student = StudentModel(id=student_id, **student_data)
            status_code = 201

        db.session.add(student)
        db.session.commit()
        return student, status_code
