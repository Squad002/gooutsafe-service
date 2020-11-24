from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker

import requests


@write_request_breaker
def register_authority(authority):
    res = requests.post(
        f"{current_app.config['URL_API_USER']}authorities",
        json=authority,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code == 201


@read_request_breaker
def get_authority_by_id(id):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}authorities?id={id}", timeout=(3.05, 9.1)
    )
    return res.json()[0]


@read_request_breaker
def get_authority_by_email(email):
    res = requests.get(
        f"{current_app.config['URL_API_USER']}authorities?email={email}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.json()[0] if res.json() else None


@read_request_breaker
def login_authority(email, password):
    res = requests.post(
        f"{current_app.config['URL_API_USER']}authorities/login",
        json={"email": email, "password": password},
    )

    return res.json()["message"] == "Success"
