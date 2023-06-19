from collections import namedtuple

import pytest

from db import db
from models import CourseModel, CourseRegisterModel, StudentModel, TutorModel

StubData = namedtuple("StubData", "course register student tutor")


@pytest.fixture(scope="function")
def populate_db_with_stub_data(app):
    course_data = {"name": "English", "subject_type": "11+ exam", "id": 1, "summary": None, "test_providers": None}
    student_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "jphill111",
        "password": "password",
        "summary": "Looking for a tutor",
        "id": 1,
        "profile_picture": None,
    }
    tutor_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "username": "jphill111",
        "password": "password",
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


def test_register_students_and_tutors_in_course(populate_db_with_stub_data, client):
    """
    This test uses a preloaded database to test the addition of students and tutors to a course_register
    In order to check the validity of this test we need to manipulate the raw student and tutor data to remove the
    password field. This is desired as we should not ever provide a password in the json response of a call to
    get course registers.

    """
    expected_student_entry = populate_db_with_stub_data.student.copy()
    expected_student_entry.pop("password")

    expected_tutor_entry = populate_db_with_stub_data.tutor.copy()
    expected_tutor_entry.pop("password")

    tutor_response = client.post("/tutors/1/course_registers/1")
    assert tutor_response.status_code == 201
    student_response = client.post("/students/1/course_registers/1")
    assert student_response.status_code == 201

    course_registers_response = client.get("/course_registers").json
    assert len(course_registers_response) == 1
    course_register_entity = client.get("/course_registers/1").json
    expected_course_register_entity = {
        "course": populate_db_with_stub_data.course,
        "students": [expected_student_entry],
        "tutors": [expected_tutor_entry],
        "name": populate_db_with_stub_data.register["name"],
        "id": populate_db_with_stub_data.register["id"],
    }
    assert course_register_entity == expected_course_register_entity
