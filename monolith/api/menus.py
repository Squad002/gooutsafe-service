from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker

import requests

@write_request_breaker
def register_menu(menu):
    res = requests.post(
        f"{current_app.config['URL_API_RESTAURANT']}menus",
        json=menu,
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )

    return res.status_code


@read_request_breaker
def menu_sheet(menu_id):
    res = requests.get(
        f"{current_app.config['URL_API_RESTAURANT']}menus/{menu_id}",
        timeout=(
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        ),
    )
    
    if res.status_code == 404:
        return None

    return res.json()
