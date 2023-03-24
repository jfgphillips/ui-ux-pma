from flask import Flask
from flask_smorest import Api

from resources.course import blp as CourseBlueprint
from resources.student import blp as StudentBlueprint
from resources.course_register import blp as CourseRegisterBlueprint


app = Flask(__name__)

app.config["PROPAGATE_EXCEPTION"] = True
app.config["API_TITLE"] = "Tutoring REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

api.register_blueprint(CourseBlueprint)
api.register_blueprint(CourseRegisterBlueprint)
api.register_blueprint(StudentBlueprint)


if __name__ == "__main__":
    app.run(debug=True)
