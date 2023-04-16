import json
import logging

import requests
from flask import request, url_for, redirect, render_template, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt

from resources.auth import TokenManager
from resources.student import Student, StudentList
from resources.tutor import Tutor, TutorList

blp = Blueprint("Routes", __name__, description="html operations")

logger = logging.getLogger(__name__)

@blp.route("/login")
def login():
    print("start")
    jwt = verify_jwt_in_request(optional=True)
    print(jwt)
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
    user_type = request.form["user_type"]
    payload = _convert_form_to_json_payload(request.form, ["user_type"])
    if user_type == "tutor":
        response = requests.post(f"{request.url_root}{url_for('Auth.TutorLogin')}", data=payload)

    elif user_type == "student":
        response = requests.post(f"{request.url_root}{url_for('Auth.StudentLogin')}", data=payload)

    if response.status_code == 200:
        authed_response = TokenManager.generate_response(response.json()["access_token"], response.json()["refresh_token"])
        return authed_response

    return redirect(url_for("Routes.login"))


@blp.route("/homepage")
def homepage(user=None):
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        payload = get_jwt()
        id = payload["sub"]
        if payload["user_type"] == "tutor":
            user = Tutor.get(id).json

        elif payload["user_type"] == "student":
            user = Student.get(id).json

    return render_template("homepage.html", user=user)

@blp.route("/user_info")
def user_info():
    user = None
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        payload = get_jwt()
        id = payload["sub"]
        if payload["user_type"] == "tutor":
            user = Tutor.get(id).json

        elif payload["user_type"] == "student":
            user = Student.get(id).json

        return render_template("user_info.html", user=user, user_type=payload["user_type"])

    return render_template("login_form.html")


def _convert_form_to_json_payload(form: dict, exclude: list = None):
    as_dict = dict(form)
    if exclude:
        for item in exclude:
            as_dict.pop(item)
        return as_dict

    return as_dict


@blp.post("/user/update")
@jwt_required(locations=["cookies"])
def user_update():
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
    jwt = verify_jwt_in_request(optional=True)
    if jwt:
        return homepage()

    return render_template("register_form.html")

@blp.post("/handle_signup")
def handle_signup():
    user_type = request.form["user_type"]
    payload = _convert_form_to_json_payload(request.form, ["user_type"])
    if user_type == "student":
        response = requests.post(f"{request.url_root}{url_for('Students.StudentList')}", data=payload)

    elif user_type == "tutor":
        response = requests.post(f"{request.url_root}{url_for('Tutors.TutorList')}", data=payload)

    if response.status_code == 201:
        return redirect(url_for("Routes.login"))

    return render_template("register_form.html")

