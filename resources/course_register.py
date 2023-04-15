
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import CourseRegisterModel, CourseModel, StudentModel, TutorModel
from schemas import CourseRegisterSchema, CourseRegisterAndStudentSchema, CourseRegisterAndTutorSchema

blp = Blueprint("CourseRegisters", "course_registers", description="Operations on course registers")

@blp.route("/courses/<string:course_id>/course_registers")
class RegistersInCourse(MethodView):
    @blp.response(200, CourseRegisterSchema(many=True))
    def get(self, course_id):
        course = CourseModel.query.get_or_404(course_id)
        return course.registers.all()

    @blp.arguments(CourseRegisterSchema)
    @blp.response(201, CourseRegisterSchema)
    def post(self, course_register_data, course_id):
        if CourseRegisterModel.query.filter(CourseRegisterModel.course_id==course_id, CourseRegisterModel.name == course_register_data["name"]).first():
            abort(400, message="a course register with that name already exists in that course")
        course_register = CourseRegisterModel(**course_register_data, course_id=course_id)
        try:
            db.session.add(course_register)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course_register

@blp.route("/course_registers")
class CourseRegisterList(MethodView):

    @blp.response(200, CourseRegisterSchema(many=True))
    def get(self):
        return CourseRegisterModel.query.all()

    @blp.arguments(CourseRegisterSchema)
    @blp.response(201, CourseRegisterSchema)
    def post(self, course_register_data):
        course_register = CourseRegisterModel(**course_register_data)
        try:
            db.session.add(course_register)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course_register


@blp.route("/students/<string:student_id>/course_registers/<string:course_register_id>")
class LinkCourseRegistersToStudents(MethodView):
    @blp.response(201, CourseRegisterSchema)
    def post(self, student_id, course_register_id):
        student = StudentModel.query.get_or_404(student_id)
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)

        student.registers.append(course_register)
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course_register

    @blp.response(200, CourseRegisterAndStudentSchema)
    def delete(self, student_id, course_register_id):
        student = StudentModel.query.get_or_404(student_id)
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)

        student.registers.remove(course_register)
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return {"message": "student removed from course", "student": student, "course_register": course_register}

@blp.route("/tutors/<string:tutor_id>/course_registers/<string:course_register_id>")
class LinkCourseRegistersToTutors(MethodView):
    @blp.response(201, CourseRegisterSchema)
    def post(self, tutor_id, course_register_id):
        tutor = TutorModel.query.get_or_404(tutor_id)
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)

        tutor.registers.append(course_register)
        try:
            db.session.add(tutor)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course_register

    @blp.response(200, CourseRegisterAndTutorSchema)
    def delete(self, tutor_id, course_register_id):
        tutor = StudentModel.query.get_or_404(tutor_id)
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)

        tutor.registers.remove(course_register)
        try:
            db.session.add(tutor)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return {"message": "tutor removed from course", "tutor": tutor, "course_register": course_register}


@blp.route("/course_registers/<string:course_register_id>")
class CourseRegister(MethodView):
    @blp.response(200, CourseRegisterSchema)
    def get(self, course_register_id):
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)
        return course_register

    def delete(self, course_register_id):
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)
        if course_register.students:
            abort(400, message="there are students enrolled on this course")

        db.session.delete(course_register)
        db.session.commmit()
        return {"message": "course register deleted"}
