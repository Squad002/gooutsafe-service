from flask import current_app
from monolith import redis_client
from monolith.services.breakers import read_request_breaker
from json import dumps, loads

# from types import SimpleNamespace
import requests


# TODO Delete after everything is moved out and the cache mechanism is used in restaurants

@read_request_breaker
def get_users():
    users = redis_client.get("restaurants")

    if users:
        users = loads(users)
        current_app.logger.info("Using cached responses to serve restaurants")
    else:
        res = requests.get(
            f"{current_app.config['URL_API_USER']}users", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ))
        users = res.json()
        redis_client.setex("restaurants", 300, dumps(users))

    return users


@read_request_breaker
def get_user_by_id(id):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}users?id={id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json()[0]


@read_request_breaker
def get_user_by_email(email):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}users?email={email}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    if res:
        # user = loads(dumps(res.json()[0]), object_hook=lambda d: SimpleNamespace(**d))
        return res.json()[0]

    return None


@read_request_breaker
def get_operator_by_id(id):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}operators?id={id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json()[0]


@read_request_breaker
def login(email, password):
    res = requests.post(
        f"{current_app.config['URL_API_USER']}users/login",
        json={"email": email, "password": password},
    )

    return res.json()["message"] == "Success"
