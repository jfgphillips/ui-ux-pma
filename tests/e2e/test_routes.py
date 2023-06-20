import pytest
from flask import url_for


@pytest.mark.skip()
def test_signup_and_login_user(live_server, page):
    page.goto(url_for("Routes.homepage", _external=True))
    page.get_by_role("button", name="Register").click()
    page.get_by_role("textbox", name="username").fill("test_user")
    page.get_by_role("textbox", name="password").fill("password")
    page.get_by_role("textbox", name="example@gmail.com").fill("test_user@gmail.com")
    page.get_by_role("tabpanel", name="Student").get_by_placeholder("Jon Doe").fill("Test User")
    page.get_by_role("tabpanel", name="Student").get_by_placeholder("10").fill("11")
    page.screenshot(path="screenshots/signup.png")
    page.get_by_role("button", name="Sign Up").click()
    page.screenshot(path="screenshots/login.png")
    page.get_by_role("textbox", name="username").fill("test_user")
    page.get_by_role("textbox", name="password").fill("password")
    page.get_by_role("button", name="Log in").click()
    page.get_by_role("link", name="Edit Profile").click()

