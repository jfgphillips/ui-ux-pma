import os

from flask import Flask
from flask_smorest import Api

from db import db
from resources import CourseRegisterBlueprint, CourseBlueprint, StudentBlueprint, TutorBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTION"] = True
    app.config["API_TITLE"] = "Tutoring REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    api = Api(app)

    with app.app_context():
        db.create_all()

    api.register_blueprint(CourseBlueprint)
    api.register_blueprint(CourseRegisterBlueprint)
    api.register_blueprint(StudentBlueprint)
    api.register_blueprint(TutorBlueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
