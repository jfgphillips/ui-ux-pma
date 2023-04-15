from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import TutorModel
from schemas import TutorSchema, TutorUpdateSchema

blp = Blueprint("Tutors", __name__, description="Operations on Tutors")


@blp.route("/tutors")
class TutorList(MethodView):
    @blp.response(200, TutorSchema(many=True))
    def get(self):
        return TutorModel.query.all()

    @blp.arguments(TutorSchema)
    @blp.response(201, TutorSchema)
    def post(self, student_data):
        tutor = TutorModel(**student_data)

        try:
            db.session.add(tutor)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an internal error occured please inspect: {e}")

        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when adding tutor to db: {e}")

        return tutor


@blp.route("/tutors/<string:tutor_id>")
class Tutor(MethodView):
    @blp.response(200, TutorSchema)
    def get(self, tutor_id):
        tutor = TutorModel.query.get_or_404(tutor_id)
        return tutor

    def delete(self, tutor_id):
        tutor = TutorModel.query.get_or_404(tutor_id)
        db.session.delete(tutor)
        db.session.commit()
        return {"message": "tutors deleted"}

    @blp.arguments(TutorUpdateSchema)
    @blp.response(204, TutorSchema)
    def put(self, tutor_data, tutor_id):
        tutor = TutorModel.query.get(tutor_id)
        if tutor:
            for key, value in tutor_data.items():
                setattr(tutor, key, value)
            status_code = 200

        else:
            tutor = TutorModel(id=tutor_id, **tutor_data)
            status_code = 201

        db.session.add(tutor)
        db.session.commit()

        return tutor, status_code
