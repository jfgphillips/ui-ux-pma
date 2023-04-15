from db import db


class TutorModel(db.Model):
    __tablename__ = "Tutors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    summary = db.Column(db.String)
    profile_picture = db.Column(db.String)

    registers = db.relationship("CourseRegisterModel", back_populates="tutors", secondary="TutorRegister")