from collections import namedtuple

import pytest
import testing.postgresql
from flask_jwt_extended import create_access_token

from app import create_app
from db import db
from models import CourseModel, CourseRegisterModel, StudentModel, TutorModel


@pytest.fixture(scope="function")
def app():
    postgresql = testing.postgresql.Postgresql()
    app = create_app(postgresql.url())
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        db.create_all()

    # other setup can go here

    yield app

    with app.app_context():
        db.drop_all()

    postgresql.stop()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def admin_authed_header(app):
    with app.app_context():
        access_token = create_access_token("admin_user", additional_claims={"user_type": "admin"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers



StubData = namedtuple("StubData", "course register student tutor")


@pytest.fixture(scope="function")
def populate_db_with_student_and_tutor_data(app, client):
    student_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "student123",
        "password": "student_password",
        "summary": "Looking for a tutor",
        "profile_picture": None,
    }
    tutor_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "tutor123",
        "password": "tutor_password",
        "summary": "I am a tutor",
        "profile_picture": None,
    }
    StudentModel(**student_data)
    TutorModel(**tutor_data)
    client.post("/students", data=student_data)
    client.post("/tutors", data=tutor_data)

    return StubData(student=student_data, tutor=tutor_data, register=None, course=None)


@pytest.fixture(scope="function")
def populate_db_with_stub_data(app):
    course_data = {"name": "English", "subject_type": "11+ exam", "id": 1, "summary": None, "test_providers": None}
    student_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "jphill111",
        "password": "student_password",
        "summary": "Looking for a tutor",
        "id": 1,
        "profile_picture": None,
    }
    tutor_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "jphill111",
        "password": "tutor_password",
        "summary": "I am a tutor",
        "id": 1,
        "profile_picture": None,
    }

    course_register_data = {"name": "my first course", "course_id": 1, "id": 1}

    course = CourseModel(**course_data)
    student = StudentModel(**student_data)
    tutor = TutorModel(**tutor_data)
    register = CourseRegisterModel(**course_register_data)
    with app.app_context():
        db.session.add(course)
        db.session.add(register)
        db.session.add(student)
        db.session.add(tutor)
        db.session.commit()

    return StubData(course=course_data, register=course_register_data, student=student_data, tutor=tutor_data)
