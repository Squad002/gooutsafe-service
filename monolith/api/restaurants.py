from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker

import requests


@write_request_breaker
def register_restaurant(restaurant):
    res = requests.post(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants",
        json=restaurant,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code


@read_request_breaker
def get_restaurant_by_id(id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants?id={id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json()[0]


def permissions(operator_id, restaurant_id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants/{restaurant_id}/permissions?operator_id={operator_id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.status_code