import pytest
from flask_jwt_extended import create_access_token


def student_authed_header(student_id, app):
    # FIXME
    with app.app_context():
        access_token = create_access_token(student_id, additional_claims={"user_type": "student"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers


def tutor_authed_header(tutor_id, app):
    # FIXME
    with app.app_context():
        access_token = create_access_token(tutor_id, additional_claims={"user_type": "tutor"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers
