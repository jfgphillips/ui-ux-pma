from db import db
from sqlalchemy import ARRAY


class CourseRegisterModel(db.Model):
    __tablename__ = "CourseRegisters"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("Courses.id"), nullable=False)
    student_ids = db.Column(db.Integer, db.ForeignKey("Students.id"), nullable=False)  # TODO: swap with array postgress

    course = db.relationship("CourseModel", back_populates="registrations")
    student = db.relationship("StudentModel", back_populates="registrations")
