import jwt
import pytest

from constants import JWT_SECRET_KEY


@pytest.mark.parametrize(
    "login_data, endpoint, expected_identity, expected_user_type",
    [
        ({"data": {"username": "student123", "password": "student_password"}}, "students/login", 1, "student"),
        ({"data": {"username": "tutor123", "password": "tutor_password"}}, "tutors/login", 1, "tutor"),
        ({"json": {"username": "admin", "password": "password"}}, "admin/login", 0, "admin"),
    ],
)
def test_token_generation(
    login_data, endpoint, expected_identity, expected_user_type, client, populate_db_with_student_and_tutor_data
):
    """
    This test validates that jwt payloads are correctly formatted for both students and tutors with multiple input
    formats (json + data). The test uses a fixture (populate_db_with_student_and_tutor_data) to prepopulate the testing
    database with some student and tutor data.
    The control flow of this test is as follows:
    1. use the flask test client to make a post request against the desired login endpoint.
    2. assert that the request was processed correctly
    3. decode the jwt token
    4. validate that the jwt token has the expected payload fields (user id, user_type)
    4. check that the token is fresh (recently generated)
    """
    response = client.post(endpoint, **login_data)
    assert response.status_code == 200
    tokens = response.json
    jwt_payload = jwt.decode(tokens["access_token"], key=JWT_SECRET_KEY, algorithms="HS256")
    assert jwt_payload["sub"] == expected_identity
    assert jwt_payload["user_type"] == expected_user_type
    assert jwt_payload["fresh"]  # Check the payload is fresh


@pytest.mark.parametrize(
    "login_data, endpoint",
    [
        ({"data": {"username": "student123", "password": "invalid_password"}}, "students/login"),
        ({"data": {"username": "tutor123", "password": "invalid_password"}}, "tutors/login"),
        ({"json": {"username": "admin", "password": "invalid_password"}}, "admin/login"),
    ],
)
def test_invalid_credentials(login_data, endpoint, populate_db_with_student_and_tutor_data, client):
    """
    This test validates that users that have not been authenticated correctly against the respective endpoints get
    jwt tokens. Similar to the above test, this uses a flask test client with populated test data. In this example
    however, we do not provide the correct login credentials for a user and expect authorisation errors.
    The test is validated given the API response 401 (Unauthorised)
    """
    response = client.post(endpoint, **login_data)
    assert response.status_code == 401
