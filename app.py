import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, get_jwt, set_access_cookies
from flask_migrate import Migrate
from flask_smorest import Api

from blocklist import BLOCKLIST
from constants import JWT_SECRET_KEY, UPLOAD_FOLDER
from db import db
from resources import (
    AuthBlueprint,
    CourseBlueprint,
    CourseRegisterBlueprint,
    RoutesBlueprint,
    StudentBlueprint,
    TutorBlueprint,
)
from resources.auth import TokenManager, TokenRefresh


def create_app(db_url=None):
    load_dotenv()
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
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    db.init_app(app)
    Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_CSRF_CHECK_FORM"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return TokenManager.unset_jwt()

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "invalid_token"}),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"description": "The token has been revoked.", "error": "token_revoked"}),
            401,
        )

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=15))
            if target_timestamp > exp_timestamp:
                refresh_response = TokenRefresh.post()
                set_access_cookies(response, refresh_response.access_token)
            return response

        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    api.register_blueprint(CourseBlueprint)
    api.register_blueprint(StudentBlueprint)
    api.register_blueprint(TutorBlueprint)
    api.register_blueprint(CourseRegisterBlueprint)
    api.register_blueprint(AuthBlueprint)
    api.register_blueprint(RoutesBlueprint)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="192.168.50.14", port=5001)
