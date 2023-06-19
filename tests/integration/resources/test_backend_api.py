import pytest
from flask_jwt_extended import create_access_token


@pytest.mark.parametrize(
    "endpoint, create_data_kwargs, update_data_kwargs, update_data_key",
    [
        (
            "/students",
            {
                "data": {
                    "name": "john Phillips",
                    "age": 11,
                    "email": "jfgp111@gmail.com",
                    "username": "jphill111",
                    "password": "password",
                    "summary": "Looking for a tutor",
                }
            },
            {"json": {"age": 10}},
            "age",
        ),
        (
            "/tutors",
            {
                "data": {
                    "name": "john Phillips",
                    "age": 20,
                    "email": "jfgp111@gmail.com",
                    "username": "jphill111",
                    "password": "password",
                    "summary": "I am a tutor",
                }
            },
            {"json": {"summary": "I am a good tutor"}},
            "summary",
        ),
        (
            "/courses",
            {"json": {"name": "English", "subject_type": "11+ exam"}},
            {"json": {"subject_type": "Humanities"}},
            "subject_type",
        ),
    ],
    ids=["student test", "tutor test", "courses test"],
)
def test_create_update_delete_roundtrip(
    endpoint, create_data_kwargs, update_data_kwargs, update_data_key, client, admin_authed_header
):
    """
    The following test round trips the endpoints for a particular resource following the general structure:
    1. check no entities exist
    2. post a new entity
    3. check 1 entity exists
    4. check created entity matches with the arguments provided
    5. update the existing entity with a put request
    6. check 1 entity exists
    7. check the updated field is correctly saved
    8. authorise the client to perform deletes
    9. delete entity
    10. check entity successfully deleted

    n.b. the entities tested are independent of one another.

    :param endpoint: the endpoint used by the client
    :param create_data_kwargs: the data used to create an entity in the database
    :param update_data_kwargs: the data used to update an entity in the database
    :param update_data_key: the key of the data that was updated
    :param client: a flask `test_client`

    Observations:
    `/students` and `/tutors` endpoints use `form` data to create entities and json to update entities. '/courses' uses
    json for both create and update. This should be standardised to `data` or `json`.

    `status_codes` are standardised across the endpoints showing http request contracts have been standardised

    The `delete` endpoints are protected using @jwt_required where `/students` and `/tutors` require `user_type` to equal
    `admin` or match the `id` of the calling client deleting their account. This is an issue if e.g. a student can access
    the jwt protected tutor endpoint where the id matches an existing tutor id. Here a student is able to delete a tutor
    account that is not theirs.
    For a reproducible example see `test_delete_identity_bug`

    Though the `/courses` endpoint is protected, it is not selective as to which users are allows to perform this action

    One cannot simply authorise a client using any jwt access_token. We require the flask `app.app_context()` which
    prevents malicious actors from actioning destructive operations.

    Actions:
    1. Standarise communication to use the same payload locations for request data across `/students`, `/tutors` and
       `/courses`

    2. Decide who is able to delete courses; should it be a tutor or only with admin privileges

    """
    # assert no students present in db
    current_entities_before_request = client.get(endpoint).json
    assert len(current_entities_before_request) == 0

    # post data to the endpoint
    create_response = client.post(endpoint, **create_data_kwargs)
    entity_id = create_response.json["id"]
    assert create_response.status_code == 201

    # check that there is one entity in the db
    current_entities_after_create = client.get(endpoint).json
    assert len(current_entities_after_create) == 1

    # use the id from the response to query for the created_entity
    created_entity = client.get(f"{endpoint}/{entity_id}").json
    # check that the created entity data is correctly populated
    assert created_entity == create_response.json

    update_response = client.put(f"{endpoint}/{entity_id}", **update_data_kwargs)
    assert update_response.status_code == 200

    # check that there is still one entity in the db
    current_entities_after_update = client.get(f"{endpoint}").json
    assert len(current_entities_after_update) == 1

    # get the updated entity and check that their data has been updated with update_json
    updated_entity = client.get(f"{endpoint}/{entity_id}").json
    assert updated_entity[update_data_key] == next(iter(update_data_kwargs.values()))[update_data_key]

    delete_response = client.delete(f"{endpoint}/{entity_id}", headers=admin_authed_header)
    assert delete_response.status_code == 200

    current_entities_after_delete = client.get(f"{endpoint}").json
    assert len(current_entities_after_delete) == 0


def test_delete_identity_bug(client, app):
    """
    This test shows the entity bug here we create a student and a tutor in the database. The student and tutor entities
    coincidentally have the same id's; if we authorise the client with the student_id and call delete on a tutor we
    will delete the tutor entity and not the student entity (our original intention)

    actions:
    in order to fix this we can check that the calling client has the correct user type. e.g. for the student endpoint
    @jwt_required()
    def delete(self, student_id):
        jwt_payload = get_jwt()
        if jwt_payload["user_type"] == "admin" or (jwt_payload["sub"] == student_id and jwt_payload["user_type"] == "student"):
            student = StudentModel.query.get_or_404(student_id)
            db.session.delete(student)
            db.session.commit()
            return {"message": "deleted student"}

        abort(401, message="you are not allowed to delete other accounts")
    """
    student_response = client.post(
        "/students",
        data={
            "name": "john Phillips",
            "age": 11,
            "email": "jfgp111@gmail.com",
            "username": "jphill111",
            "password": "password",
            "summary": "Looking for a tutor",
        },
    )
    tutor_response = client.post(
        "/tutors",
        data={
            "name": "john Phillips",
            "age": 11,
            "email": "jfgp111@gmail.com",
            "username": "jphill111",
            "password": "password",
            "summary": "I am a tutor",
        },
    )
    assert tutor_response.status_code == 201
    with app.app_context():
        access_token = create_access_token(student_response.json["id"], additional_claims={"user_type": "student"})
        headers = {"Authorization": "Bearer {}".format(access_token)}
        delete_response = client.delete(f"/tutors/{student_response.json['id']}", headers=headers)
        assert delete_response.status_code == 200

    student_response_after_delete = client.get(f"/students/{student_response.json['id']}")
    tutor_response_after_delete = client.get(f"/tutors/{tutor_response.json['id']}")
    assert tutor_response_after_delete.status_code == 404
    assert student_response_after_delete.status_code == 200


def test_course_register(client):
    """
    This test looks to create a course, and a course register using the course ID.
    :param client:
    """
    create_course_response = client.post("/courses", json={"name": "English", "subject_type": "11+ exam"})
    assert create_course_response.status_code == 201
    course_id = create_course_response.json["id"]

    create_course_register_response = client.post(f"/courses/{course_id}/course_registers", json={"name": "my_course"})
    assert create_course_register_response.status_code == 201
    current_course_registers = client.get("/course_registers").json

    expected_course_data = create_course_response.json
    expected_course_data.pop("registers")

    assert len(current_course_registers) == 1
    assert current_course_registers[0]["course"] == expected_course_data
