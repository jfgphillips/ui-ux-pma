from db import db

class TutorRegister(db.Model):
    __tablename__ = "TutorRegister"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("Tutors.id"))
    course_register_id = db.Column(db.Integer, db.ForeignKey("CourseRegisters.id"))
