import os
import pytest
from marshmallow import ValidationError
from dotenv import load_dotenv
import schemas


def test_student_schema_valid_data():
    data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jphillips@gmail.com",
        "username": "jphill111",
        "password": "password",
        "registers": [{"name": "my course"}],
    }
    schemas.StudentSchema().load(data=data)


@pytest.mark.parametrize(
    "data, bad_field",
    [
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "invalid email",
                "username": "jphill111",
                "password": "password",
            },
            "email",
        ),
        (
            {
                "name": "john Phillips",
                "age": "InvalidAge",
                "email": "jfgp111@gmail.com",
                "username": "jphill111",
                "password": "password",
            },
            "age",
        ),
        (
            {"name": 1111, "age": 11, "email": "jfgp111@gmail.com", "username": "jphill111", "password": "password"},
            "name",
        ),
        (
            {
                "age": 11,
                "email": "jfgp111@gmail.com",
                "username": "jphill111",
                "password": "password",
            },
            "name",
        ),
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jfgp111@gmail.com",
                "password": "password",
            },
            "username",
        ),
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jfgp111@gmail.com",
                "username": "jphill111",
            },
            "password",
        ),
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jphillips@gmail.com",
                "username": "jphill111",
                "password": "password",
                "registers": "invalid_registers",
            },
            "registers",
        ),
        (
            {
                "name": "john Phillips",
                "age": 11,
                "email": "jphillips@gmail.com",
                "username": "jphill111",
                "password": "password",
                "unknown_field": "random field",
            },
            "unknown_field",
        ),
    ],
    ids=[
        "invalid email field (email)",
        "invalid int field (age)",
        "invalid string field (name)",
        "missing name",
        "missing username",
        "missing password",
        "invalid registers",
        "unknown field",
    ],
)
def test_student_schema_raises_validation_errors(data, bad_field):
    """
    This test aims to check the validity of the marshmallow schemas. We have aimed to exhaustively test validation of a
    StudentSchema with incorrect data.
    :param data:
    :param bad_field:
    :return:
    """
    try:
        schemas.StudentSchema().load(data=data)
    except ValidationError as err:
        assert len(err.messages) == 1
        assert bad_field in err.messages


def test_student_schema_raises_nested_validation_errors():
    data = {
        "name": "john Phillips",
        "age": 11,
        "email": "jphillips@gmail.com",
        "username": "jphill111",
        "password": "password",
        "registers": [{"invalid name": "my course"}],
    }
    with pytest.raises(ValidationError):
        schemas.StudentSchema().load(data=data)


@pytest.mark.parametrize(
    "filepath",
    [
        ("files/test-schema-upload.txt"),
        ("files/test-schema-upload.png"),
        ("files/test-schema-upload.jpg"),
        ("files/test-schema-upload.csv"),
    ],
)
def test_student_schema_valid_file(filepath):
    os.chdir(os.getcwd())
    with open(filepath, "r") as f:
        data = {
            "name": "john Phillips",
            "age": 11,
            "email": "jphillips@gmail.com",
            "username": "jphill111",
            "password": "password",
            "profile_picture": f,
            "registers": [{"name": "my course"}],
        }
        schemas.StudentSchema().load(data=data)
