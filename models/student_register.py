from db import db


class StudentRegister(db.Model):
    __tablename__ = "StudentRegister"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Students.id"))
    course_register_id = db.Column(db.Integer, db.ForeignKey("CourseRegisters.id"))
