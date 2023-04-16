from dataclasses import dataclass

import requests

from flask import render_template, request, url_for, redirect, flash, make_response
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    jwt_required,
    create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from flask_smorest import Blueprint, abort
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from blocklist import BLOCKLIST
from models import StudentModel, TutorModel
from schemas import LoginSchema

blp = Blueprint("Auth", "auth", description="Authorising a user")


def get_tokens(id, user_type, is_fresh):
    additional_claims = {"user_type": user_type}
    access_token = create_access_token(identity=id, fresh=is_fresh, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=id)
    response = make_response(redirect(url_for("Routes.homepage"), 302))
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return access_token, refresh_token, response


@dataclass
class TokenManager:
    access_token: str
    refresh_token: str

    @classmethod
    def get_tokens(cls, uid, user_type, is_fresh):
        additional_claims = {"user_type": user_type}
        access_token = create_access_token(identity=uid, fresh=is_fresh, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=uid)
        return cls(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def generate_response(access_token, refresh_token):
        response = make_response(redirect(url_for("Routes.homepage"), 302))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response

    @staticmethod
    def unset_jwt():
        response = make_response(redirect(url_for("Routes.homepage"), 302))
        unset_jwt_cookies(response)
        return response


@blp.route("/students/login")
class StudentLogin(MethodView):
    @blp.arguments(LoginSchema, location="form", content_type="form")
    def post(self, login_data):
        student = StudentModel.query.filter(StudentModel.username == login_data["username"]).first()
        if student and pbkdf2_sha256.verify(login_data["password"], student.password):
            token_manager = TokenManager.get_tokens(uid=student.id, user_type="student", is_fresh=True)
            return {"access_token": token_manager.access_token, "refresh_token": token_manager.refresh_token}

        abort(401, message="Invalid credentials")


@blp.route("/tutors/login")
class TutorLogin(MethodView):
    @blp.arguments(LoginSchema, location="form", content_type="form")
    def post(self, login_data):
        tutor = TutorModel.query.filter(TutorModel.username == login_data["username"]).first()

        if tutor and pbkdf2_sha256.verify(login_data["password"], tutor.password):
            token_manager = TokenManager.get_tokens(uid=tutor.id, user_type="tutor", is_fresh=True)
            return {"access_token": token_manager.access_token, "refresh_token": token_manager.refresh_token}

        abort(401, message="Invalid credentials")


@blp.route("/admin/login")
class AdminLogin(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, login_data):
        if login_data["username"] == "admin" and login_data["password"] == "password":
            token_manager = TokenManager.get_tokens(uid=0, user_type="admin", is_fresh=True)
            return {"access_token": token_manager.access_token, "refresh_token": token_manager.refresh_token}

        abort(401, message="Invalid credentials")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        payload = get_jwt()
        id = payload["sub"]
        user_type = payload["user_type"]
        token_manager = TokenManager.get_tokens(uid=id, user_type=user_type, is_fresh=False)
        BLOCKLIST.add(payload["jti"])
        return {"access_token": token_manager.access_token}


@blp.route("/user_logout")
class Logout(MethodView):
    @jwt_required(locations=["cookies"])
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200
