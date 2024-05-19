from collections import namedtuple

import pytest

StubData = namedtuple("StubData", "course register student tutor")


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


def test_get_registers_in_course(populate_db_with_stub_data, client):
    """
    This test checks that stub data can be used to access the courses endpoint
    we are expecting that the expected data from the api request for course_registers endpoint
    matches that from the raw data used to populate the database
    """
    course_id = populate_db_with_stub_data.course["id"]
    response = client.get(f"courses/{course_id}/course_registers")
    expected_course_data = populate_db_with_stub_data.course.copy()

    assert response.status_code == 200
    assert response.json[0]["course"] == expected_course_data


def test_roundtrip_subscribe_unsubscribe_student(populate_db_with_stub_data, client):
    """This test aims to roundtrip the flow of a student subscribing and unsubscribing from a course
    The flow proceeds as follows
    1. access the student id from the stub data
    2. ensure that the student is not registered on any courses
    3. register the student on a course
    4. ensure the student is registered on one course
    5. ensure that the course that student registerd on in the database matches the one we submitted
    6. delete the student from that course
    7. ensure that the student is no longer registered on any courses
    """
    student_id = populate_db_with_stub_data.student["id"]
    course_register_id = populate_db_with_stub_data.register["id"]
    empty_response = client.get(f"students/{student_id}/course_registers")
    assert len(empty_response.json) == 0

    successful_response = client.post(f"students/{student_id}/course_registers/{course_register_id}")
    assert successful_response.status_code == 201

    populated_response = client.get(f"students/{student_id}/course_registers")
    assert len(populated_response.json) == 1
    assert populated_response.json[0]["id"] == course_register_id

    delete_response = client.delete(f"students/{student_id}/course_registers/{course_register_id}")
    assert delete_response.status_code == 200

    empty_response_after_delete = client.get(f"students/{student_id}/course_registers")
    assert len(empty_response_after_delete.json) == 0


def test_roundtrip_subscribe_unsubscribe_tutor_bug(populate_db_with_stub_data, client):
    """
    This test roundrips a tutor. There is one inconsistency and one error in this test:
    Inconsistency
    1. The get method raises 401 instead of returning an empty list of registers from the query.
    error:
    1. A typo in the unsubscribe method (delete request) queries the `StudentModel` as opposed to the
       `TutorModel`. This causes an empty list to be returned and thus the tutor.registers.remove(course_register)
       operation raises a ValueError

    Actions:
    look to standardise the api; choose beteween raising an error and returning an empty list
    fix the `delete` endpoint to query the right model
    """
    tutor_id = populate_db_with_stub_data.tutor["id"]
    course_register_id = populate_db_with_stub_data.register["id"]
    empty_response = client.get(f"tutors/{tutor_id}/course_registers")
    assert empty_response.status_code == 401

    successful_response = client.post(f"tutors/{tutor_id}/course_registers/{course_register_id}")
    assert successful_response.status_code == 201

    populated_response = client.get(f"tutors/{tutor_id}/course_registers")
    assert len(populated_response.json) == 1
    assert populated_response.json[0]["id"] == course_register_id
    with pytest.raises(ValueError):
        client.delete(f"tutors/{tutor_id}/course_registers/{course_register_id}")


@pytest.mark.parametrize(
    "data",
    [
        (
            {
                "name": "this is a course",
                "course_id": 2,
            }
        ),
        (
            {
                "name": "this is a course",
            }
        ),
    ],
    ids=["course doesnt exist in the `CourseModel`", "no course id provided"],
)
def test_create_course_register_error(data, client):
    """
    This test checks that the `CourseRegisterModel` successfully raises errors for invalid data

    Actions:
    These errors are handled at the `db.session.commit()` stage; Some additional validation can be done
    at a higher level to prevent hitting a sqlalchemy exception.
    """
    response = client.post("/course_registers", json=data)
    assert response.status_code == 400


def test_create_course_register(client):
    """this test creates a course and a course_register for that course in the database"""
    course_data = {"name": "English", "subject_type": "11+ exam"}
    create_course_response = client.post("/courses", json=course_data)
    assert create_course_response.status_code == 201
    course_id = create_course_response.json["id"]
    course_register_data = {
        "name": "this is a course",
        "course_id": course_id,
    }
    create_course_register_response = client.post("course_registers", json=course_register_data)
    assert create_course_register_response.status_code == 201
    course_register_id = create_course_register_response.json["id"]
    course_registers_response = client.get(f"course_registers/{course_register_id}")
    assert course_registers_response.status_code == 200
    assert course_registers_response.json["course"]["id"] == course_id


def test_roundtrip_course_register(client, admin_authed_header):
    """
    This test looks to create a course, and a course register using the course ID. This test follows the pattern:
    1. create a course entity with a post to /courses
    2. extract course_id from the response.json
    3. use the course_id to create a `course_register` associated to the previously created course
    4. check that the course data is populated correctly
    5. authorise the client and delete the course_register entity
    6. assert course is correctly deleted

    """
    create_course_response = client.post("/courses", json={"name": "English", "subject_type": "11+ exam"})
    assert create_course_response.status_code == 201
    course_id = create_course_response.json["id"]

    create_course_register_response = client.post(f"/courses/{course_id}/course_registers", json={"name": "my_course"})
    assert create_course_register_response.status_code == 201
    current_course_registers = client.get("/course_registers").json
    assert len(current_course_registers) == 1

    course_register_id = current_course_registers[0]["id"]

    expected_course_data = create_course_response.json
    expected_course_data.pop("registers")

    assert len(current_course_registers) == 1
    assert current_course_registers[0]["course"] == expected_course_data

    delete_course_register_response = client.delete(
        f"/course_registers/{course_register_id}", headers=admin_authed_header
    )
    assert delete_course_register_response.status_code == 200

    course_registers_after_delete = client.get("/course_registers").json
    assert len(course_registers_after_delete) == 0


def test_create_course_register_with_duplicate_course(populate_db_with_stub_data, client):
    """This test makes sure it is not possible for us to create two course_registers for the same course"""
    course_id = populate_db_with_stub_data.course["id"]
    duplicated_course_register_data = populate_db_with_stub_data.register.copy()
    duplicated_course_register_data.pop("id")
    response = client.post(f"courses/{course_id}/course_registers", json=duplicated_course_register_data)
    assert response.status_code == 400

    course_registers_response = client.get("/course_registers")
    assert len(course_registers_response.json) == 1


def test_delete_course_failed_with_student(populate_db_with_stub_data, client, admin_authed_header):
    """This test checks that course regiseters cannot be deleted (even by admin) whilst students are registered on it"""
    student_id = populate_db_with_stub_data.student["id"]
    course_register_id = populate_db_with_stub_data.register["id"]
    subscribe_student_response = client.post(f"/students/{student_id}/course_registers/{course_register_id}")
    assert subscribe_student_response.status_code == 201

    delete_course_register_response = client.delete(
        f"course_registers/{course_register_id}", headers=admin_authed_header
    )
    assert delete_course_register_response.status_code == 400

    course_registers_response = client.get(f"/course_registers/{course_register_id}")
    assert course_registers_response.status_code == 200
    assert course_registers_response.json == subscribe_student_response.json


def test_delete_course_failed_with_tutor_bug(populate_db_with_stub_data, client, admin_authed_header):
    """
    The following test shows a bug where a course register can be deleted with tutors still enrolled

    Actions:
    standardise the course_register delete method such that it checks for the presence of tutors and students before
    allowing the deletion of the course_register
    """
    tutor_id = populate_db_with_stub_data.tutor["id"]
    course_register_id = populate_db_with_stub_data.register["id"]
    subscribe_student_response = client.post(f"/tutors/{tutor_id}/course_registers/{course_register_id}")
    assert subscribe_student_response.status_code == 201

    delete_course_register_response = client.delete(
        f"course_registers/{course_register_id}", headers=admin_authed_header
    )
    assert delete_course_register_response.status_code == 200

    course_registers_response = client.get(f"/course_registers/{course_register_id}")
    assert course_registers_response.status_code == 404
