from db import db
from sqlalchemy import ARRAY


class CourseModel(db.Model):
    __tablename__ = "Courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    subject_type = db.Column(db.String(80), unique=False)
    test_providers = db.Column(db.String)  # TODO: swap for array with postgress
    tutors = db.Column(db.Integer)
    summary = db.Column(db.String)

    registrations = db.relationship("CourseRegisterModel", back_populates="course")
