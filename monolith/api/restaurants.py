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

    if not res.json():
        return None
    else:
        return res.json()[0]


@read_request_breaker
def get_restaurants():
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json() 


@read_request_breaker
def get_restaurants_elastic(query, page=1, perpage=20):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants?query={query}&page={page}&perpage={perpage}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    print(res.json())
    return res.json()    


@read_request_breaker
def operator_restaurants_list(operator_id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}restaurants?operator_id={operator_id}", timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )
    return res.json()


@write_request_breaker
def register_review(review):
    res = requests.post(
        f"{current_app.config['URL_API_RESTAURANT']}reviews",
        json=review,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code
