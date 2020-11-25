from flask import current_app
from monolith.services.breakers import read_request_breaker, write_request_breaker
from datetime import date, datetime
from monolith import api

import requests



@write_request_breaker
def make_booking(confirmed_booking, end_booking, restaurant_id, seats, start_booking, user_id):
    booking = {
        "confirmed_booking": confirmed_booking,
        "end_booking": end_booking,
        "restaurant_id": restaurant_id,
        "seats": seats,
        "start_booking": start_booking, 
        "user_id": user_id,
    }
    
    res = requests.post(
        f"{current_app.config['URL_API_BOOKING']}bookings",
        json = booking,
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res

@read_request_breaker
def get_booking_by_id(booking_number):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}bookings?booking_number={booking_number}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    if not res.json():
        return res.json()
    else:
        return res.json()[0]


@write_request_breaker
def confirm_booking(users_list):
    res = requests.post(
        f"{current_app.config['URL_API_BOOKING']}booking/confirm",
        json = users_list,
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res


@read_request_breaker
def user_booking_list(user_id):
    res = requests.get(
        f"{current_app.config['URL_API_BOOKING']}bookings?user_id={user_id}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    restaurants_bookings_list = []
    for booking in res.json():
        start_booking = datetime.strptime(booking["start_booking"], "%Y-%m-%dT%H:%M:%SZ")
        if datetime.date(start_booking) >= date.today():
            restaurant = api.get_restaurant_by_id(booking["restaurant_id"])
            restaurants_bookings_list.append((booking,restaurant))

    return restaurants_bookings_list


@write_request_breaker
def delete_booking(user_id, booking_number):
    res = requests.delete(
        f"{current_app.config['URL_API_BOOKING']}bookings/{booking_number}?user_id={user_id}",
        timeout = (
            current_app.config["READ_TIMEOUT"],
            current_app.config["WRITE_TIMEOUT"],
        )
    )

    return res.status_code


