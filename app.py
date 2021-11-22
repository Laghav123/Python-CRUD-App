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
import os

app = Flask(__name__)

from pymongo import MongoClient

m_client = MongoClient()
db = m_client["user-database"]
creds = db.creds
AUTH_COOKIE = None
from pathlib import Path

DB = os.path.join(Path(__file__).absolute().parent, "unt.json")


class LagError(Exception):
    pass


class NotAuth(Exception):
    pass


def return_success(msg):
    return {"status": "Success", "message": msg}


def return_failure(msg):
    return {"status": "Failure", "message": msg}


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
    with open(DB, "r") as f:
        try:
            data = json.load(f)
        except JSONDecodeError as e:
            data = []
    return data


def write_data_to_db(data):
    with open(DB, "w") as f:
        json.dump(data, f)


@app.errorhandler(500)
def internal_error(error):
    return redirect(url_for("home")), 500


def j_add_document(new_item):
    data = get_data_from_db()
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


def j_update_document(old, new):
    data = get_data_from_db()
    try:
        data.remove(old)
        data.append(new)
    except ValueError as e:
        raise LagError("Register first")
    write_data_to_db(data)


def m_update_document(old, new):
    m_remove_document(old)
    m_add_document(new)


@app.route(endpoints.EDIT_USER, methods=["POST"])
def edit_user():
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
    correct_password = "admin123"
    password = request.form.get("password")
    if password == correct_password:
        resp = make_response(redirect(url_for("dashboard")))
        resp.set_cookie("pw", gen_cookie(), max_age=None)
        return resp
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
        return redirect(url_for("home")), 403

    return render_template("dashboard.html")
