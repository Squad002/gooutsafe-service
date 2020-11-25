from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker

import requests


@write_request_breaker
def register_table(table):
    res = requests.post(
        f"{current_app.config['URL_API_RESTAURANT']}tables",
        json=table,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code


@write_request_breaker
def patch_table(table, id):
    res = requests.patch(
        f"{current_app.config['URL_API_RESTAURANT']}tables/{id}",
        json=table,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code    


@write_request_breaker
def remove_table(table_id):
    res = requests.delete(
        f"{current_app.config['URL_API_RESTAURANT']}tables/{table_id}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code   


@read_request_breaker
def tables_list(restaurant_id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}tables?restaurant_id={restaurant_id}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.json()


@read_request_breaker
def get_table_by_id(table_id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}tables/{table_id}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    if res.status_code == 200:
        return res.json()
    else:
        return None