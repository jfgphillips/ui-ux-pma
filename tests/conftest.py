from collections import namedtuple

import pytest
import testing.postgresql
from flask_jwt_extended import create_access_token

from app import create_app
from db import db
from models import CourseModel, CourseRegisterModel, StudentModel, TutorModel


@pytest.fixture(scope="function")
def app():
    """
    This is a fixture implemented in conftest to setup a fake postgres database for testing purposes
    It is generally good practice to set up fake databases for testing pipelines that have sufficient setup/teardown
    flows. The fixture works as follows
    1. use the testing postgresql library to setup a temporary postgres db instance + connection
    2. provide this db url during flask app initialisation
    3. set the app config to testing mode
    4. within the app_context manager initialise sqlachemy db object (containing all model (table) schemas) to create
       all tables
    5. yield the app object during testing scope
    6. tear down the app object by dropping all the tables
    7. close postgres connection
    """
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
    """A fixture used to yield a flask test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def admin_authed_header(app):
    """A fixture used to generate an admin authed header for accessing jwt enabled endpoints as the admin user"""
    with app.app_context():
        access_token = create_access_token("admin_user", additional_claims={"user_type": "admin"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers


StubData = namedtuple("StubData", "course register student tutor")


@pytest.fixture(scope="function")
def populate_db_with_student_and_tutor_data(app, client):
    """
    A fixture used to populate the database with student and tutor stub data; stored in conftest for use across the
    testing estate
    (currently required for unit.resources.test_auth)
    """
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
    """
    Use fixtures to populate the database with some stub data; stored in conftest for use across the entire testing
    estate
    (currently required for tests in the unit.resources.test_course_register)
    """
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
