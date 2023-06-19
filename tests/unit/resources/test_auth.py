import pytest
import jwt

from constants import JWT_SECRET_KEY


@pytest.mark.parametrize(
    "login_data, endpoint, expected_identity, expected_user_type",
    [
        ({"username": "student123", "password": "student_password"}, "students/login", 1, "student"),
        ({"username": "tutor123", "password": "tutor_password"}, "tutors/login", 1, "tutor"),
    ],
)
def test_token_generation(
    login_data, endpoint, expected_identity, expected_user_type, client, populate_db_with_student_and_tutor_data
):
    response = client.post(endpoint, data=login_data)
    assert response.status_code == 200
    tokens = response.json
    jwt_payload = jwt.decode(tokens["access_token"], key=JWT_SECRET_KEY, algorithms="HS256")
    assert jwt_payload["sub"] == expected_identity
    assert jwt_payload["user_type"] == expected_user_type


@pytest.mark.parametrize(
    "login_data, endpoint",
    [
        ({"username": "student123", "password": "invalid_password"}, "students/login"),
        ({"username": "tutor123", "password": "invalid_password"}, "tutors/login"),
    ],
)
def test_invalid_credentials(login_data, endpoint, populate_db_with_student_and_tutor_data, client):
    response = client.post(endpoint, data=login_data)
    assert response.status_code == 401
