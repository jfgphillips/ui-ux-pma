import pytest
from sqlalchemy.exc import IntegrityError
from tests.client_headers import get_student_authed_header

from db import db
from models import StudentModel


@pytest.fixture(scope="function")
def stub_tutor_data(app):
    """This is a fixture used to populate the testing database with some dummy student data"""
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
    student = StudentModel(**student_data)
    with app.app_context():
        db.session.add(student)
        db.session.commit()
    return student_data


def test_student_delete_error(stub_tutor_data, client, app):
    """
    This test aims to assure that the logic used to ensure the caller is permissioned to delete an account functions
    as expected. The flow runs as follows
    1. with a populated db containing a student make a delete request to the students endpoint using a different
       student id
    2. assert we get a bad response (401)
    3. sanity check that we still have the student in the database
    """
    expected_student_data = stub_tutor_data.copy()
    expected_student_data.pop("password")
    expected_student_data["registers"] = []

    student_id = stub_tutor_data["id"]
    different_student_id = 2
    assert different_student_id != student_id
    bad_response = client.delete(
        f"/students/{student_id}", headers=get_student_authed_header(student_id=different_student_id, app=app)
    )
    assert bad_response.status_code == 401
    students_response = client.get(f"/students/{student_id}")
    assert students_response.status_code == 200
    assert students_response.json == expected_student_data


def test_student_delete_success(stub_tutor_data, client, app):
    """
    This test aims to check that the student containing the correct credentials can delete their account.
    We can sanity check this operation by requesting the deleted students data and getting a 404 error indicating there
    is no entity.
    """
    student_id = stub_tutor_data["id"]
    good_response = client.delete(
        f"/students/{student_id}", headers=get_student_authed_header(student_id=student_id, app=app)
    )
    assert good_response.status_code == 200
    students_response = client.get(f"/students/{student_id}")
    assert students_response.status_code == 404


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
                "summary": "Looking for a tutor",
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
                "summary": "Looking for a tutor",
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
                "summary": "Looking for a tutor",
                "profile_picture": None,
            },
            409,
        ),
    ],
    ids=["sql integrity error", "marshmallow schema error", "unique username error"],
)
def test_student_create_errors_inconsistencies_bug(bad_data, status_code, stub_tutor_data, client):
    """
    This test shows the inconsistencies between the different validation steps of the students post method which causes
    different `response.status_code`'s to be returned.

    1. sql integrity error raised in the `StudentModel` when attempting to add non-unique fields:
       models/student.py
       ```
       email = db.Column(db.String, unique=True, nullable=False)
       ```
    2. breaks the `PlainStudentSchema`:
       schemas.py
       ```
       name = fields.Str(required=True)
       ```
    3. breaks at this line in the post method:
       resources/student.py
       ```
       StudentModel.query.filter(StudentModel.username == student_data["username"]).first():
       ```
    n.b.
    The different mechanisms used to validate data introduces unintended variability in the response codes
    (409) (400) and (409) in order for us to standardise the messages returned from the api, we should enforce
    validation in only one place or standardise the response codes returned.
    """
    bad_response = client.post("/students", data=bad_data)
    assert bad_response.status_code == status_code

    students_response = client.get("/students").json
    assert len(students_response) == 1


def test_student_update_constraint_error_bug(stub_tutor_data, client):
    """
    This test will does create a student as stated by the docstring. There are two reasons for this
    1. StudentUpdateSchema prevents passing username and password to the put method
    2. the StudentModel requires a username and password to be present in the created Student Object
       Because step 1 prevents these fields a student can never be created

    Actions:
    Allow student update schema to contain password and username fields or constrain; this may be desirable when a
    client wants to update their password and username. Constraints must be implemented here to check that the
    username is not already taken by another user.

    A better error messages should be used when passing incomplete student data as opposed to the existing integrity
    error that is raised upon db.session.commit() in order not to break the python script. This should allow for a
    graceful blow up.
    """
    bad_data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jfgp111@gmail.com",
        "summary": "Looking for a tutor",
    }
    with pytest.raises(IntegrityError):
        client.put("/students/2", json=bad_data)

    students_response = client.get("/students").json
    assert len(students_response) == 1
