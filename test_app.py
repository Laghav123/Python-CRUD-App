from collections import UserDict
from flask import json
from flask.scaffold import F
from pymongo import database
from pymongo.mongo_client import MongoClient
import pytest
import endpoints
from app import app
import os
from pathlib import Path
import flask
from flask.testing import FlaskClient

FC: FlaskClient
FR = flask.Response

DB = os.path.join(Path(__file__).absolute().parent, "unt.json")
mongo_db = "mongodb://localhost:27017/"
mongoc = MongoClient(mongo_db)
user_database = mongoc["user-database"]["creds"]


@pytest.fixture
def client():
    yield app.test_client()


@pytest.fixture(autouse=True)
def magic_clear_db():

    # with open(DB, "w") as f:
    #     f.write("[]")
    user_database.delete_many({})
    yield
    # with open(DB, "r") as f:
    #     print(f.read())
    # with open(DB, "w") as f:
    #     f.write("[]")
    user_database.delete_many({})


def test_add_details(client):
    user = {"email": "laghav@gmail.com", "password": "abcdlaghav"}
    user_database.delete_many({})
    response: FR = client.post(endpoints.ADD_USER, data=user)
    assert response.get_json()["status"] == "Success"
    assert user_database.find_one(user) is not None
    response: FR = client.post(endpoints.ADD_USER, data=user)
    assert response.get_json()["status"] == "Failure"
    assert user_database.find_one(user) is not None
    assert user_database.count_documents(user) == 1


def test_multi_user_add(client):
    user1 = {"email": "1", "password": "1p"}
    user2 = {"email": "2", "password": "2p"}
    client.post(endpoints.ADD_USER, data=user1)
    client.post(endpoints.ADD_USER, data=user2)
    assert user_database.find_one(user1) is not None
    assert user_database.find_one(user2) is not None
    assert user_database.count_documents(user1) == 1
    assert user_database.count_documents(user2) == 1


def test_delete_user(client):
    # Test starts, DB is empty.
    user = {"email": "2", "password": "2p"}
    # Try to delete a non existent user.
    response: FR = client.post(endpoints.DELETE_USER, data=user)
    # assert that failure is returned
    assert response.get_json()["status"] == "Failure"
    # add a user
    client.post(endpoints.ADD_USER, data=user)
    # try to delete a present user
    response: FR = client.post(endpoints.DELETE_USER, data=user)
    # assert that success is returned
    assert response.get_json()["status"] == "Success"


def test_edit_details(client):
    user = {"email": "laghav1@gmail.com", "password": "abcdlaghav1"}
    response: FR = client.post(
        endpoints.EDIT_USER,
        data={
            "email": "laghav1@gmail.com",
            "password": "abcdlaghav1",
            "new_password": "abcdlaghav2",
        },
    )
    assert response.get_json()["status"] == "Failure"

    client.post(endpoints.ADD_USER, data=user)
    response: FR = client.post(
        endpoints.EDIT_USER,
        data={
            "email": "laghav1@gmail.com",
            "password": "abcdlaghav0",
            "new_password": "abcdlaghav2",
        },
    )
    assert response.get_json()["status"] == "Failure"
    response: FR = client.post(
        endpoints.EDIT_USER,
        data={
            "email": "laghav1@gmail.com",
            "password": "abcdlaghav1",
            "new_password": "abcdlaghav2",
        },
    )
    assert response.get_json()["status"] == "Success"

    assert user_database.find_one(
        {"email": "laghav1@gmail.com", "password": "abcdlaghav2"}
    )
    assert (
        user_database.count_documents(
            {"email": "laghav1@gmail.com", "password": "abcdlaghav2"}
        )
        == 1
    )
