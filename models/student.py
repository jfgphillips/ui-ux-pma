from db import db


class StudentModel(db.Model):
    __tablename__ = "Students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String)

    registrations = db.relationship("CourseRegisterModel", back_populates="student")
