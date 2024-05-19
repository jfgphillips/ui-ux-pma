from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import CourseModel, CourseRegisterModel, StudentModel, TutorModel
from schemas import CourseRegisterAndStudentSchema, CourseRegisterAndTutorSchema, CourseRegisterSchema

blp = Blueprint("CourseRegisters", "course_registers", description="Operations on course registers")


@blp.route("/courses/<int:course_id>/course_registers")
class RegistersInCourse(MethodView):
    @blp.response(200, CourseRegisterSchema(many=True))
    def get(self, course_id):
        course = CourseModel.query.get_or_404(course_id)
        print(course.registers)
        return course.registers.all()

    @blp.arguments(CourseRegisterSchema)
    @blp.response(201, CourseRegisterSchema)
    def post(self, course_register_data, course_id):
        if CourseRegisterModel.query.filter(
            CourseRegisterModel.course_id == course_id, CourseRegisterModel.name == course_register_data["name"]
        ).first():
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


@blp.route("/students/<int:student_id>/course_registers")
class RegistersInStudent(MethodView):
    @staticmethod
    @blp.response(200, CourseRegisterSchema(many=True))
    def get(student_id):
        """
        For a given student ID, retrieve the events associated with that student
        :param student_id:
        :return: list of events for the student
        """
        student = StudentModel.query.get_or_404(student_id)
        if not student:
            abort(401, message="student not registered on a course")
        return student.registers


@blp.route("/tutors/<int:tutor_id>/course_registers")
class RegistersInTutor(MethodView):
    @staticmethod
    @blp.response(200, CourseRegisterSchema(many=True))
    def get(tutor_id):
        """
        For a given tutor ID, retrieve the events associated to that tutor
        :param tutor_id: db id of the tutor
        :return a list of events for the tutor
        """
        tutor = TutorModel.query.get_or_404(tutor_id)
        if not tutor.registers:
            abort(401, message="tutors not registered on a course")
        return tutor.registers


@blp.route("/course_registers")
class CourseRegisterList(MethodView):
    """used for operations on events"""

    @staticmethod
    @blp.response(200, CourseRegisterSchema(many=True))
    def get():
        """retrieves a list of all events in the database"""
        return CourseRegisterModel.query.all()

    @blp.arguments(CourseRegisterSchema)
    @blp.response(201, CourseRegisterSchema)
    def post(self, course_register_data):
        """used to create an event in the database"""
        course_register = CourseRegisterModel(**course_register_data)
        try:
            db.session.add(course_register)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an integrity error occured please inspect: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when saving course to db {e}")

        return course_register


@blp.route("/students/<int:student_id>/course_registers/<int:course_register_id>")
class LinkCourseRegistersToStudents(MethodView):
    """This is used to link Students to Events"""

    @blp.response(201, CourseRegisterSchema)
    def post(self, student_id, course_register_id):
        """
        Used to enrol students on a course
        :param student_id: the db id of a student
        :param course_register_id: the db id of an event created for a course
        """
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
        """used to remove a student from an event"""
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


@blp.route("/tutors/<int:tutor_id>/course_registers/<int:course_register_id>")
class LinkCourseRegistersToTutors(MethodView):
    @blp.response(201, CourseRegisterSchema)
    def post(self, tutor_id, course_register_id):
        """
        used to enrol tutors on a course
        :param tutor_id: the db id of a tutor
        :param course_register_id: the db id of an event created for a course
        """
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
        """
        used to delete a tutor from a course
        """
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


@blp.route("/course_registers/<int:course_register_id>")
class CourseRegister(MethodView):
    @blp.response(200, CourseRegisterSchema)
    def get(self, course_register_id):
        """used to list the details of an event for a given event id"""
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)
        return course_register

    @jwt_required()
    def delete(self, course_register_id):
        """used to delete an event for a givent event id"""
        course_register = CourseRegisterModel.query.get_or_404(course_register_id)
        if course_register.students:
            abort(400, message="there are students enrolled on this course")

        db.session.delete(course_register)
        db.session.commit()
        return {"message": "course register deleted"}
