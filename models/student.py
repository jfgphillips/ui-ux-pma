from db import db


class StudentModel(db.Model):
    __tablename__ = "Students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String)
    profile_picture = db.Column(db.String)

    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    registers = db.relationship("CourseRegisterModel", back_populates="students", secondary="StudentRegister")
    # courses = db.relationship("CourseModel", back_populates="students", secondary="CourseRegisters")

