from flask_jwt_extended import create_access_token


def get_student_authed_header(student_id, app):
    with app.app_context():
        access_token = create_access_token(student_id, additional_claims={"user_type": "student"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers


def get_tutor_authed_header(tutor_id, app):
    with app.app_context():
        access_token = create_access_token(tutor_id, additional_claims={"user_type": "tutor"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers
