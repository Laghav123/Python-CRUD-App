from flask import Flask, request, redirect, url_for, abort
from flask.helpers import make_response
from flask.json import JSONEncoder, jsonify
from flask.templating import render_template
from json.decoder import JSONDecodeError
from logging import error
from sys import implementation
import endpoints
import json
import pymongo
import random

app = Flask(__name__)

from pymongo import MongoClient

m_client = MongoClient()
db = m_client["user-database"]
creds = db.creds
AUTH_COOKIE = None


class LagError(Exception):
    pass


class NotAuth(Exception):
    pass


def return_success(msg):
    return {"status": "Success", "message": msg}


def return_failure(msg):
    return {"status": "Failure", "message": msg}


# TODO_DONE write a POST method to accept email and password
# TODO_DONE write those email pass to a file (later to be replaced with DB)


def gen_cookie() -> str:
    global AUTH_COOKIE
    if AUTH_COOKIE is not None:
        return AUTH_COOKIE
    gen: random.SystemRandom = random.SystemRandom()
    all = [str(gen.randrange(0, 9)) for x in range(64)]
    AUTH_COOKIE = "".join(all)
    return AUTH_COOKIE


def validate_cookie(cookie):
    global AUTH_COOKIE
    if cookie == None:
        raise NotAuth("Not authenticated")
    if AUTH_COOKIE != cookie:
        raise NotAuth("Not authenticated.")


def get_data_from_db():
    with open("/Users/laghavmohan/Desktop/server/unt.json", "r") as f:
        try:
            data = json.load(f)
        except JSONDecodeError as e:
            data = []
    return data


def write_data_to_db(data):
    with open("/Users/laghavmohan/Desktop/server/unt.json", "w") as f:
        json.dump(data, f)


@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for("home")), 500


def j_add_document(new_item):
    data = get_data_from_db()
    # TODO send error if user already present.
    if new_item in data:
        raise LagError("Already Registered")
    data.append(new_item)
    write_data_to_db(data)


def m_add_document(new_item):

    if creds.find_one({"email": new_item["email"]}) is not None:
        raise LagError("Already registered.")

    creds.insert_one(new_item)


@app.route(endpoints.ADD_USER, methods=["POST"])
def add_user():
    try:
        validate_cookie(request.cookies.get("pw"))
    except NotAuth as e:
        return return_failure(str(e))
    # TODO if cookie not valid, redirect user to home page.
    email = request.form["new_user_email"]
    password = request.form["new_user_password"]

    try:
        m_add_document(new_item={"email": email, "password": password})
    except LagError as e:
        return return_failure(str(e))
    return return_success("Successfully added")


def j_remove_document(to_delete):
    data = get_data_from_db()
    try:
        data.remove(to_delete)
    except ValueError as e:
        raise LagError("You are not in the list")
    print(data)
    write_data_to_db(data)


def m_remove_document(to_delete):
    result = creds.delete_one(to_delete)
    if result.deleted_count != 1:
        raise LagError("User Not present")


# TODO_DONE write deleter to delete email pass pair from that file.
# TODO_DONE check if email exists, if not, error.
@app.route(endpoints.DELETE_USER, methods=["POST"])
def delete_user():
    try:
        validate_cookie(request.cookies.get("pw"))
    except NotAuth as e:
        return return_failure(str(e))
    email = request.form["deleting_email"]
    password = request.form["deleting_password"]

    try:
        m_remove_document({"email": email, "password": password})
    except LagError as e:
        return return_failure(str(e))
    return return_success("Successfully Deleted")


# TODO_DONE write edit method to change email or password in that file said above.
# TODO_DONE check if email exists already or not. if not, return error


def j_update_document(old, new):
    data = get_data_from_db()
    try:
        data.remove(old)
        data.append(new)
    except ValueError as e:
        raise LagError("Register first")
        # pass
    write_data_to_db(data)


def m_update_document(old, new):
    # creds.update
    m_remove_document(old)
    m_add_document(new)


@app.route(endpoints.EDIT_USER, methods=["POST"])
def edit_user():
    # TODO if cookie not valid, redirect user to home page.
    try:
        validate_cookie(request.cookies.get("pw"))
    except NotAuth as e:
        return return_failure(str(e))
    email = request.form["edit_user_email"]
    password = request.form["edit_user_password"]
    new_password = request.form["new_password"]

    try:
        m_update_document(
            old={"email": email, "password": password},
            new={"email": email, "password": new_password},
        )
    except LagError as e:
        return return_failure(str(e))
    return return_success("Edited successfully")


# TODO auth today?


@app.route("/upper", methods=["POST"])
def upper():
    text = request.form["text"]
    processed_text = text.upper()
    return processed_text

    # Do you see ths ?


@app.route(endpoints.EMPTY)
@app.route(endpoints.HOME)
def home():
    try:
        validate_cookie(request.cookies.get("pw"))
    except NotAuth:
        resp = make_response(render_template("index.html"))
        resp.set_cookie("pw", "", expires=0)
        return resp

    return redirect(url_for("dashboard"))


@app.route(endpoints.LOGIN, methods=["GET", "POST"])
def login_admin():
    # Check password correctness.
    # if correct
    # - set a cookie.
    # - redirect to dashboard.
    correct_password = "admin123"
    password = request.form.get("password")
    if password == correct_password:
        resp = make_response(redirect(url_for("dashboard")))
        resp.set_cookie("pw", gen_cookie(), max_age=None)
        return resp
    # if not, redirect back to home.
    else:
        return redirect(url_for("home"))


@app.route(endpoints.LOGOUT)
def logout():
    global AUTH_COOKIE
    AUTH_COOKIE = None
    return redirect(url_for("home"))


@app.route(endpoints.DASH)
def dashboard():
    try:
        validate_cookie(request.cookies.get("pw"))
    except NotAuth as e:
        return return_failure(str(e))

    return render_template("dashboard.html")


@app.route("/about_us")
def about_us():
    return "we are here"


# #  write a new method that takes GET "text" param. and returns a json object.


# @app.route("/jayson", methods=["GET"])
# def jayson():
#     input_text: str = request.args.get("text")
#     import json

#     # with open("/Users/laghavmohan/Desktop/server/unt.json", "w") as f:
#     #     json.dump(
#     #         [
#     #             {"username": "blah", "password": "blahp"},
#     #             {"username": "foo", "password": "foop"},
#     #         ],
#     #         f,
#     #     )
#     # with open("/Users/laghavmohan/Desktop/server/unt.json", "r") as f:
#     #     data = json.load(f)
#     #     print(data)

#     return jsonify({"response": input_text.upper()})  # this returns json.


# @app.route("/add_numbers", methods=["POST"])
# def add_numbers():
#     n1 = int(request.form["n1"])
#     n2 = int(request.form["n2"])
#     return return_success(str(n1 + n2))


# @app.route("/divide_numbers", methods=["POST"])
# def divide_numbers():
#     n1 = int(request.form["n1"])
#     n2 = int(request.form["n2"])
#     if n2 == 0:
#         return return_failure("Indefinate value")

#     return return_success(str(float(n1) / float(n2)))
