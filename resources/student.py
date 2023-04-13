from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StudentModel
from schemas import StudentSchema, StudentUpdateSchema

blp = Blueprint("Students", __name__, description="Operations on students")


@blp.route("/students")
class StudentList(MethodView):
    @blp.response(200, StudentSchema(many=True))
    def get(self):
        return StudentModel.query.all()

    @blp.arguments(StudentSchema)
    @blp.response(201, StudentSchema)
    def post(self, student_data):
        student = StudentModel(**student_data)

        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")

        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when adding student to db: {e}")

        return student


@blp.route("/students/<string:student_id>")
class Student(MethodView):
    @blp.response(200, StudentSchema)
    def get(self, student_id):
        student = StudentModel.query.get_or_404(student_id)
        return student

    def delete(self, student_id):
        student = StudentModel.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return {"message": "student deleted"}

    @blp.arguments(StudentUpdateSchema)
    @blp.response(204, StudentSchema)
    def put(self, student_data, student_id):
        student = StudentModel.query.get(student_id)
        if student:
            for key, value in student_data.items():
                setattr(student, key, value)

        else:
            student = StudentModel(id=student_id, **student_data)

        db.session.add(student)
        db.session.commit()

        return student
