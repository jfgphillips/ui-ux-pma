from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from db import db
from models import TutorModel
from schemas import TutorSchema, TutorUpdateSchema, LoginSchema

blp = Blueprint("Tutors", __name__, description="Operations on Tutors")


@blp.route("/tutors")
class TutorList(MethodView):
    @staticmethod
    @blp.response(200, TutorSchema(many=True))
    def get():
        return TutorModel.query.all()

    @staticmethod
    @blp.arguments(TutorSchema, location="form", content_type="form")
    @blp.response(201, TutorSchema)
    def post(tutor_data):
        print(tutor_data)
        if TutorModel.query.filter(TutorModel.username == tutor_data["username"]).first():
            abort(409, message="a student with that username already exists")

        tutor_data["password"] = pbkdf2_sha256.hash(tutor_data["password"])

        tutor = TutorModel(**tutor_data)

        try:
            db.session.add(tutor)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"an internal error occured please inspect: {e}")

        except SQLAlchemyError as e:
            abort(500, message=f"an error occured when adding tutor to db: {e}")

        return tutor


@blp.route("/tutors/<int:tutor_id>")
class Tutor(MethodView):
    """
    This class handles queries on students given a tutor ID
    """

    @staticmethod
    @blp.response(200, TutorSchema)
    def get(tutor_id):
        """used to retrieve a single tutor from the database"""
        tutor = TutorModel.query.get_or_404(tutor_id)
        return tutor

    @jwt_required()
    def delete(self, tutor_id):
        """used to delete a tutor from the database"""
        jwt_payload = get_jwt()
        if jwt_payload["user_type"] == "admin" or jwt_payload["sub"] == tutor_id:
            tutor = TutorModel.query.get_or_404(tutor_id)
            db.session.delete(tutor)
            db.session.commit()
            return {"message": "tutors deleted"}

        abort(401, message="you are not permissioned to delete other accounts")

    @blp.arguments(TutorUpdateSchema)
    @blp.response(204, TutorSchema)
    def put(self, tutor_data, tutor_id):
        """used to update tutor data from the database, if tutor isn't present, we create the tutor"""
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
