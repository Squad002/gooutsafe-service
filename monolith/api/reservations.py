from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker
from datetime import date, datetime

import requests


@read_request_breaker
def reservations_list_by_restaurant_id_date(restaurant_id, start_day):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}reservations?restaurant_id={restaurant_id}&start_day={start_day}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.json()

@read_request_breaker
def check_permission(booking_number, operator_id, restaurant_id):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}reservations/booking_number={booking_number}&operator_id={operator_id}&restaurant_id={restaurant_id}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return True if res.status_code != 200 else False


@write_request_breaker
def confirm_checkin(checkin_list):
    print()
    res = requests.post(
        f"{current_app.config['URL_API_BOOKING']}reservations/checkin",
        json = checkin_list,
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res


@read_request_breaker
def booking_and_checkin(booking_number):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}bookings/{booking_number}/checkin",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.json()


@read_request_breaker
def get_users_reservation(booking_number):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}reservations/{booking_number}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.json() 

@write_request_breaker
def delete_reservation(booking_number):
    res = requests.delete(
        f"{current_app.config['URL_API_BOOKING']}reservations/{booking_number}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.status_code