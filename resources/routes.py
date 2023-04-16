import logging

import requests
from flask import request, url_for, redirect, render_template, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt

from resources.auth import TokenManager
from resources.student import Student
from resources.tutor import Tutor

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
    payload = {
        "username": request.form["username"],
        "password": request.form["password"]
    }
    if user_type == "tutor":
        response = requests.post(f"{request.url_root}{url_for('Auth.TutorLogin')}", data=payload)

    elif user_type == "student":
        response = requests.post(f"{request.url_root}{url_for('Auth.StudentLogin')}", data=payload)

    if response.status_code == 200:
        authed_response = TokenManager.generate_response(response.json()["access_token"], response.json()["refresh_token"])
        return authed_response

    return redirect(url_for("Routes.login"))


@blp.route("/homepage")
def homepage():
    user = None
    jwt = verify_jwt_in_request(optional=True)
    print(jwt)
    if jwt:
        print(jwt)
        payload = get_jwt()
        id = payload["sub"]
        if payload["user_type"] == "tutor":
            user = Tutor.get(id).json

        elif payload["user_type"] == "student":
            user = Student.get(id).json

    return render_template("homepage.html", user=user)