from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker

import requests


@write_request_breaker
def register_operator(operator):
    res = requests.post(
        f"{current_app.config['URL_API_USER']}operators",
        json=operator,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code == 201


@read_request_breaker
def get_operator_by_id(id):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}operators?id={id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json()[0]


@write_request_breaker
def delete_operator(id):
    res = requests.delete(
        f"{current_app.config['URL_API_USER']}operators/{id}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code == 204


@read_request_breaker
def get_operator_by_email(email):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}operators?email={email}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.json()[0] if res.json() else None


@read_request_breaker
def login_operator(email, password):
    res = requests.post(
        f"{current_app.config['URL_API_USER']}operators/login",
        json={"email": email, "password": password},
    )

    return res.json()["message"] == "Success"
