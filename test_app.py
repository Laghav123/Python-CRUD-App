from collections import UserDict
from flask import json
from flask.scaffold import F
from pymongo import database
from pymongo.mongo_client import MongoClient
import pytest
import endpoints
from app import app

# from flaskr.db import init_db
import flask
from flask.testing import FlaskClient

FC: FlaskClient
FR = flask.Response

DB = "/Users/laghavmohan/Desktop/server/unt.json"
mongo_db = "mongodb://localhost:27017/"
mongoc = MongoClient(mongo_db)
user_database = mongoc["user-database"]["creds"]


@pytest.fixture
def client():
    # db_fd, db_path = tempfile.mkstemp()
    # app = create_app({'TESTING': True})
    yield app.test_client()
    # with app.test_client() as client:
    #     # with app.app_context():
    #     #     # init_db()
    #     #     pass
    #     yield client

    # os.close(db_fd)
    # os.unlink(db_path)


@pytest.fixture(autouse=True)
def magic_clear_db():

    # Before test
    with open(DB, "w") as f:
        f.write("[]")
    user_database.delete_many({})
    # test happens
    yield
    # After test
    # with open(DB, "r") as f:
    #     print(f.read())
    with open(DB, "w") as f:
        f.write("[]")
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

    # assert response.get_json()["status"] == "Success"
    # with open(DB, "r") as f:
    #     data = json.load(f)
    #     assert user in data
    # response: FR = client.post(endpoints.ADD_USER, data=user)
    # # assert duplicate didn't get added.
    # assert response.get_json()["status"] == "Failure"
    # assert response.get_json()["message"] == "Already Registered"
    # print(response)


def test_multi_user_add(client):
    user1 = {"email": "1", "password": "1p"}
    user2 = {"email": "2", "password": "2p"}
    # post request
    client.post(endpoints.ADD_USER, data=user1)
    client.post(endpoints.ADD_USER, data=user2)
    # check if both users done or not.
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


def test_garbage(client):
    from pymongo import MongoClient

    cl = MongoClient()
    col = cl["test-database"]
    # insert a document to the db
    post = {"name": "Laghav", "class": "5th"}
    posts = col.posts
    post_id = posts.insert_one(post).inserted_id
    post_id
    # find all documentsof collection
    # [print(x) for x in col.posts.find()]
    # # update a documentof collection
    # col.posts.update({"name": "Ankit"}, {"$set": {"class": "10th"}})
    # [print(x) for x in col.posts.find()]
    # delete a documentof collection

    col.posts.delete_one({"name": "Ankit"})


def test_adder(client):
    response: FR = client.post("/add_numbers", data={"n1": 7, "n2": 5})
    assert response.get_json()["message"] == "12"
    print(response.get_json())


def test_divider(client):
    response: FR = client.post("/divide_numbers", data={"n1": 12, "n2": 5})
    assert response.get_json()["message"] == "2.4"
    assert response.get_json()["status"] == "Success"
    response: FR = client.post("/divide_numbers", data={"n1": 12, "n2": 0})
    assert response.get_json()["message"] == "Indefinate value"
    assert response.get_json()["status"] == "Failure"


def test_about_us(client):
    response: FR = client.get("/about_us")
    print(response.data)
    assert response is not None
    print(response)


def test_home(client):
    response: FR = client.get("/")
    print(response.data)
    assert response is not None
    assert response.get_data() == b"<p>Hello, World!</p>"
    print(response)


def blah(name: str, email: str):
    pass


def test_upper(client):
    response: FR = client.post("/upper", data={"text": "laghav"})
    print(response.mimetype)
    assert response.get_data() == b"LAGHAV"


def test_jayson(client):
    # This "data" parameter is wrong it seems.
    response = client.get("/jayson?text=laghav")
    # response: FR = client.get("/jayson", data={
    #     "text": "laghav"
    # })
    assert response.is_json
    assert response.get_json() == {"response": "LAGHAV"}
