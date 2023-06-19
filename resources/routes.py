import json
import logging
from typing import Optional

import requests
from flask import request, url_for, redirect, render_template, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt

from resources.auth import TokenManager
from resources.course import CourseList
from resources.course_register import CourseRegisterList, CourseRegister, RegistersInStudent, RegistersInTutor
from resources.student import Student, StudentList
from resources.tutor import Tutor, TutorList
from resources.utils import File

blp = Blueprint("Routes", __name__, description="html operations")

logger = logging.getLogger(__name__)


@blp.route("/")
def root():
    """Redirects users to /homepage"""
    return redirect(url_for("Routes.homepage"))


@blp.route("/homepage")
def homepage():
    """
    Handles the displayed homepage logic; gets the current and populates. If there is a jwt token the user will
    be retrieved and their information populated on the login page.
    """
    user = None
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        payload = get_jwt()
        id = payload["sub"]
        if payload["user_type"] == "tutor":
            user = Tutor.get(id).json

        elif payload["user_type"] == "student":
            user = Student.get(id).json

    # populate sections with data
    tutors = TutorList.get().json
    courses = CourseList.get().json
    students = StudentList.get().json
    events = CourseRegisterList.get().json

    return render_template("homepage.html", user=user, tutors=tutors, events=events, students=students, courses=courses)


@blp.route("/login")
def login():
    """Actions the request to login, redirects user to the login form."""
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        return homepage()

    return render_template("login_form.html")


@blp.route("/logout")
@jwt_required(locations=["cookies"])
def logout():
    requests.post(f"{request.url_root}{url_for('Auth.Logout')}")
    deauthed_response = TokenManager.unset_jwt()

    return deauthed_response


@blp.post("/handle_login")
def handle_login():
    """
    Handles the login e.g. student or tutor, if success we redirect to the homepage with a logged in state
    else we regenerate the login form to try again.
    """
    response = None
    user_type = request.form["user_type"]
    payload = _convert_form_to_json_payload(request.form, ["user_type"])
    if user_type == "tutor":
        response = requests.post(f"{request.url_root}{url_for('Auth.TutorLogin')}", data=payload)

    elif user_type == "student":
        response = requests.post(f"{request.url_root}{url_for('Auth.StudentLogin')}", data=payload)

    if response.status_code == 200:
        authed_response = TokenManager.generate_response(
            response.json()["access_token"], response.json()["refresh_token"]
        )
        return authed_response

    return redirect(url_for("Routes.login"))


@blp.route("/user_info")
def user_info():
    """Renders the users information such that a user can login, if not logged in it redirects to the login form."""
    user = None
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        payload = get_jwt()
        uid = payload["sub"]
        if payload["user_type"] == "tutor":
            user = Tutor.get(uid).json

        elif payload["user_type"] == "student":
            user = Student.get(uid).json

        return render_template("user_info.html", user=user, user_type=payload["user_type"])

    return render_template("login_form.html")


def _convert_form_to_json_payload(form: dict, exclude: Optional[list] = None):
    """Helper method to convert form to a raw json data payload"""
    as_dict = dict(form)
    if exclude:
        for item in exclude:
            as_dict.pop(item)
        return as_dict

    return as_dict


@blp.post("/handle_update")
@jwt_required(locations=["cookies"])
def user_update():
    """Handles the submission from the /user_info endpoint."""
    user_payload = get_jwt()
    uid = user_payload["sub"]
    form_payload = _convert_form_to_json_payload(request.form)
    if user_payload["user_type"] == "tutor":
        response = Tutor.put(tutor_id=uid, tutor_data=form_payload)

    elif user_payload["user_type"] == "student":
        response = Student.put(student_id=uid, student_data=form_payload)

    if response.status_code in [200, 201]:
        return redirect(url_for("Routes.homepage", user=response.json))

    return redirect(url_for("Routes.user_info"))


@blp.route("/signup")
def signup():
    """Renders a register form such that a user can sign up."""
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        return homepage()

    return render_template("register_form.html")

@blp.post("/handle_signup")
def handle_signup():
    """Handles the response from a register form and actions the appropriate endpoints, if the signup responds with a
    success then the user is redirected to the login page, otherwise the user is redirected to signup again."""
    response = None
    file_upload = None
    user_type = request.form["user_type"]
    print(request.files)
    payload = _convert_form_to_json_payload(request.form, ["user_type", "profile_picture"])
    file_payload = {"profile_picture": request.files, "user_type": user_type}

    if user_type == "student":
        response = requests.post(f"{request.url_root}{url_for('Students.StudentList')}", data=payload)

    elif user_type == "tutor":
        response = requests.post(f"{request.url_root}{url_for('Tutors.TutorList')}", data=payload)

    if response and response.status_code == 201:
        return redirect(url_for("Routes.login"))

    return render_template("register_form.html")


@blp.route("/list_fields/<string:type>", methods=["GET", "POST"])
def list_fields(type):
    """
    A generic form that can list the contents of any table in the database or from another endpoint.
    Databases:
    Tutors, Students, Subjects, Courses,

    Endpoints:
    /my_people
    /my_courses
    """
    fields = None
    if type == "tutor":
        fields = TutorList.get().json

    elif type == "course":
        fields = CourseList.get().json

    elif type == "student":
        fields = StudentList.get().json

    else:
        fields = CourseRegisterList.get().json

    if fields is None:
        redirect(url_for("Routes.homepage"))

    return render_template("list.html", fields=fields, type=type)


@blp.route("/detail", methods=["GET", "POST"])
def detail():
    """Used on click to display summary information on a user"""
    args = request.args
    return render_template("detail.html", name=args["name"], summary=args.get("summary"), type=args["type"])


@blp.get("/my_people")
@jwt_required(locations=["cookies"])
def my_people():
    """protected, uses jwt token to check what type of user is calling this method
    :returns
        students if the user is a `tutor`
        tutors if the user is a `student`
    """
    response = None
    type = None
    register_ids = []
    jwt_payload = get_jwt()
    uid = jwt_payload["sub"]
    if jwt_payload["user_type"] == "student":
        type = "My Tutors"
        response = RegistersInStudent.get(student_id=uid)

    elif jwt_payload["user_type"] == "tutor":
        type = "My Students"
        response = RegistersInTutor.get(tutor_id=uid)

    if response and response.status_code == 200:
        # TODO: implement this properly in the backend to remove this horrible logic
        desired_fields = []
        for raw_json in response.response:
            json_data = json.loads(raw_json)
            for json_item in json_data:
                if jwt_payload["user_type"] == "tutor":
                    desired_fields.append(json_item.get("students"))
                elif jwt_payload["user_type"] == "student":
                    desired_fields.append(json_item.get("tutors"))

        flat_list = [item for sublist in desired_fields for item in sublist]
        return render_template("list.html", fields=flat_list, type=type)

    return redirect(url_for("Routes.homepage"))


@blp.get("/my_courses")
@jwt_required(locations=["cookies"])
def my_courses():
    """
    protected, uses jwt token to check what type of user is calling this method
    Returns courses associated with a user
    :returns
        students if the user is a `tutor`
        tutors if the user is a `student`
    """
    response = None
    type = "My Courses"
    register_ids = []
    jwt_payload = get_jwt()
    uid = jwt_payload["sub"]
    if jwt_payload["user_type"] == "student":
        response = RegistersInStudent.get(student_id=uid)

    elif jwt_payload["user_type"] == "tutor":
        response = RegistersInTutor.get(tutor_id=uid)

    if response and response.status_code == 200:
        # TODO: implement this properly in the backend to remove this horrible logic
        desired_fields = []
        for raw_json in response.response:
            json_data = json.loads(raw_json)
            for json_item in json_data:
                print(json_item)
                desired_fields.append(json_item.get("course"))

        return render_template("list.html", fields=desired_fields, type=type)

    return redirect(url_for("Routes.homepage"))


@blp.post("/delete_account")
@jwt_required(locations=["cookies"])
def delete_account():
    """Used to delete account"""
    raise NotImplementedError(
        "Deletion of accounts is not supported yet, to do this use the API methods in the swagger UI or postman"
    )
