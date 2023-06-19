import pytest
from flask_jwt_extended import create_access_token

from app import create_app
import testing.postgresql
from sqlalchemy import create_engine

from db import db


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
