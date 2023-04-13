import logging

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import CourseRegisterModel
from schemas import CourseRegisterSchema, CourseRegisterUpdateSchema

blp = Blueprint("Course Registers", __name__, description="Operations on registers")

logger = logging.getLogger(__name__)


@blp.route("/course_registers")
class CourseRegisterList(MethodView):
    @blp.response(200, CourseRegisterSchema(many=True))
    def get(self):
        return CourseRegisterModel.query.all()

    @blp.arguments(CourseRegisterSchema)
    @blp.response(201, CourseRegisterSchema)
    def post(self, course_register_data):
        course = CourseRegisterModel(**course_register_data)
        logger.warning(f"course: {course}")
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course


@blp.route("/course_registers/<string:register_id>")
class CourseRegister(MethodView):
    @blp.response(200, CourseRegisterSchema)
    def get(self, register_id):
        course = CourseRegisterModel.query.get_or_404(register_id)
        return course

    @blp.arguments(CourseRegisterUpdateSchema)
    @blp.response(204, CourseRegisterSchema(many=True))
    def put(self, payload, register_id):
        course_register = CourseRegisterModel.query.get_or_404(register_id)

        for student in payload["students"]:
            if student in course_register["students"]:
                logger.warning("student already enrolled skipping")
                continue

            course_register.student_ids = student

        db.session.add(course_register)
        db.session.commit()

        return self.get(), 204

    def delete(self, register_id):
        course_register = CourseRegisterModel.query.get_or_404(register_id)
        db.session.delete(course_register)
        db.session.commit()
        return {"message": "course deleted"}
