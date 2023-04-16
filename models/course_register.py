from db import db


class CourseRegisterModel(db.Model):
    __tablename__ = "CourseRegisters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False)
    course_id = db.Column(db.Integer, db.ForeignKey("Courses.id"), nullable=False)

    course = db.relationship("CourseModel", back_populates="registers")
    students = db.relationship("StudentModel", back_populates="registers", secondary="StudentRegister")
    tutors = db.relationship("TutorModel", back_populates="registers", secondary="TutorRegister")
