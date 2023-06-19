import pytest
from sqlalchemy.exc import IntegrityError

from db import db
from models import TutorModel
from tests.client_headers import get_tutor_authed_header


@pytest.fixture(scope="function")
def stub_tutor_data(app):
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
    tutor = TutorModel(**tutor_data)
    with app.app_context():
        db.session.add(tutor)
        db.session.commit()
    return tutor_data

def test_student_delete_error(stub_tutor_data, client, app):
    """
    see tests/unit/resources.test_student.py::test_student_delete_error for explanation
    """
    expected_tutor_data = stub_tutor_data.copy()
    expected_tutor_data.pop("password")
    expected_tutor_data["registers"] = []

    tutor_id = stub_tutor_data["id"]
    different_tutor_id = 2
    assert different_tutor_id != tutor_id
    bad_response = client.delete(
        f"/tutors/{tutor_id}", headers=get_tutor_authed_header(tutor_id=different_tutor_id, app=app)
    )
    assert bad_response.status_code == 401
    tutor_response = client.get(f"/tutors/{tutor_id}")
    assert tutor_response.status_code == 200
    assert tutor_response.json == expected_tutor_data


def test_tutor_delete_success(stub_tutor_data, client, app):
    """
    see tests/unit/resources.test_student.py::test_tutor_delete_success for explanation
    """
    tutor_id = stub_tutor_data["id"]
    good_response = client.delete(
        f"/tutors/{tutor_id}", headers=get_tutor_authed_header(tutor_id=tutor_id, app=app)
    )
    assert good_response.status_code == 200
    tutor_response = client.get(f"/tutors/{tutor_id}")
    assert tutor_response.status_code == 404


@pytest.mark.parametrize(
    "bad_data, status_code",
    [
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jfgp111@gmail.com",
                "username": "jp123",
                "password": "password",
                "summary": "I am a tutor",
                "profile_picture": None,
            },
            400,
        ),
        (
            {
                "age": 11,
                "email": "jfgp111@gmail.com",
                "username": "jp123",
                "password": "password",
                "summary": "I am a tutor",
                "profile_picture": None,
            },
            422,
        ),
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jfgp111@gmail.com",
                "username": "jphill111",
                "password": "password",
                "summary": "I am a tutor",
                "profile_picture": None,
            },
            409,
        ),
    ],
    ids=["sql integrity error", "marshmallow schema error", "unique username error"],
)
def test_tutor_create_errors_inconsistencies_bug(bad_data, status_code, stub_tutor_data, client):
    """
    see tests/unit/resources.test_student.py::test_student_create_errors_inconsistencies_bug for explanation
    """
    bad_response = client.post("/tutors", data=bad_data)
    assert bad_response.status_code == status_code

    students_response = client.get("/tutors").json
    assert len(students_response) == 1



def test_tutor_update_constraint_error_bug(stub_tutor_data, client):
    """
    see tests/unit/resources.test_student.py::test_student_update_constraint_error_bug for explanation
    """
    bad_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "summary": "I am a tutor",
    }
    with pytest.raises(IntegrityError):
        client.put("/tutors/2", json=bad_data)

    tutors_response = client.get("/tutors").json
    assert len(tutors_response) == 1
