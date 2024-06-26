import logging

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import CourseModel
from schemas import CourseSchema, CourseUpdateSchema

blp = Blueprint("Courses", __name__, description="Operations on courses")

logger = logging.getLogger(__name__)


@blp.route("/courses")
class CourseList(MethodView):
    @staticmethod
    @blp.response(200, CourseSchema(many=True))
    def get():
        """return a list of courses present in the db"""
        return CourseModel.query.all()

    @blp.arguments(CourseSchema)
    @blp.response(201, CourseSchema)
    def post(self, course_data):
        """create a course in the db"""
        course = CourseModel(**course_data)
        logger.warning(f"course: {course}")
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course, 201


@blp.route("/courses/<int:course_id>")
class Course(MethodView):
    @blp.response(200, CourseSchema)
    def get(self, course_id):
        """given the id of a course db entry, retrieve the record"""
        course = CourseModel.query.get_or_404(course_id)
        return course

    @jwt_required()
    def delete(self, course_id):
        """given the id of a course db entry, delete the record"""
        course = CourseModel.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return {"message": "course deleted"}

    @blp.arguments(CourseUpdateSchema)
    @blp.response(200, CourseSchema)
    def put(self, course_data, course_id):
        """update the data of a course db entry, if a course isn't present, create the course entry"""
        course = CourseModel.query.get(course_id)
        if course:
            for key, value in course_data.items():
                setattr(course, key, value)
            status_code = 200

        else:
            course = CourseModel(id=course_id, **course_data)
            status_code = 201

        db.session.add(course)
        db.session.commit()

        return course, status_code
