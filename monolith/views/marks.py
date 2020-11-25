from sqlalchemy import or_
from flask import Blueprint, render_template, flash, redirect, request, session
from flask_login.utils import login_required

from monolith import db
from monolith.models import User
from monolith.services.auth import current_user, authority_required
from monolith.services.forms import AuthorityIdentifyForm
from monolith.services.background import tasks

from config import (
    mail_body_covid_19_mark,
    mail_body_covid_19_contact,
    mail_body_covid_19_operator_alert,
    mail_body_covid_19_operator_booking_alert,
)
from datetime import datetime


marks = Blueprint("marks", __name__)


@marks.route("/marks/new", methods=["GET", "POST"])
@authority_required
@login_required
def new_mark():
    status = 200
    form = AuthorityIdentifyForm()

    # alternative: if request.referrer == "http://127.0.0.1:5000/trace"
    if request.form.get("identification"):
        form.identifier.data = request.form["identification"]
        session["from_trace_route"] = True
    elif form.validate_on_submit():
        identifier = form.identifier.data
        current_authority = current_user
        user_to_mark = User.query.filter(
            or_(
                User.fiscalcode.like(identifier),
                User.email.like(identifier),
                User.phonenumber.like(identifier),
            )
        ).first()
        if not user_to_mark:
            flash("User not found.", category="error")
        else:
            mark(current_authority, user_to_mark, form.duration.data, datetime.utcnow())
            flash("User was marked.", category="success")

        if session.get("from_trace_route"):
            session.pop("from_trace_route", None)
            session["from_mark_route"] = True
            return redirect("/trace")

        return redirect("/marks/new")
    return render_template("mark.html", form=form), status


@marks.route("/trace", methods=["GET", "POST"])
@authority_required
@login_required
def trace():
    contacts = []
    form = AuthorityIdentifyForm()

    # Restore previous session data if available
    if session.get("from_mark_route"):
        session.pop("from_mark_route", None)
        prev_session_identifier = session.get("trace_identifier")
        prev_session_duration = session.get("trace_duration")
        session.pop("trace_identifier", None)
        session.pop("trace_duration", None)

        if prev_session_identifier and prev_session_duration:
            form.identifier.data = prev_session_identifier
            form.duration.data = prev_session_duration

    if form.validate_on_submit():
        identifier = form.identifier.data
        session["trace_identifier"] = identifier
        session["trace_duration"] = form.duration.data
        user = User.query.filter(
            or_(
                User.fiscalcode.like(identifier),
                User.email.like(identifier),
                User.phonenumber.like(identifier),
            )
        ).first()
        if not user:
            flash("The user was not found", category="error")
        else:
            if user.is_marked():
                contacts = trace_contacts(user, form.duration.data, send_email=False)

                if not contacts:
                    flash("The user did not have any contact", category="info")
            else:
                flash("You cannot trace a user that is not marked", category="error")

    return render_template("trace.html", form=form, contacts=contacts)


def mark(current_authority, user, duration, starting_date):
    # Authority mark user
    current_authority.mark(user, duration, starting_date=starting_date)
    db.session.commit()
    tasks.send_email(
        "You are positive to COVID-19",
        [user.email],
        mail_body_covid_19_mark.format(
            user.firstname,
            starting_date.strftime("%A %d. %B %Y"),
            current_authority.name,
        ),
    )
    trace_contacts(user, duration, send_email=True)


def trace_contacts(user, interval, send_email=False):
    contacts = []
    if user.is_marked():
        user_bookings = user.get_bookings(range_duration=interval)

        for user_booking in user_bookings:
            contacts_temp = []
            starting_time = user_booking.start_booking
            restaurant = user_booking.table.restaurant
            operator = restaurant.operator

            if user_booking.checkin:
                # Alert the operator about the past booking
                if send_email:
                    tasks.send_email(
                        f"You had a COVID-19 positive case in your restaurant {restaurant.name}",
                        [operator.email],
                        mail_body_covid_19_operator_alert.format(
                            operator.firstname,
                            starting_time.strftime("%A %d. %B %Y"),
                            restaurant.name,
                        ),
                    )

                # Check for possible contacts with other people
                restaurant_bookings = restaurant.get_bookings(starting_time)
                for b in restaurant_bookings:
                    if b.user != user:
                        contacts_temp.append(b.user)
                        if not b.user.is_marked() and send_email:
                            # Alert only the people that are not marked about the possible contact
                            tasks.send_email(
                                "Possible contact with a COVID-19 positive case",
                                [b.user.email],
                                mail_body_covid_19_contact.format(
                                    b.user.firstname,
                                    starting_time.strftime("%A %d. %B %Y"),
                                    restaurant.name,
                                ),
                            )

                if contacts_temp:
                    contacts.append({"date": starting_time, "people": contacts_temp})
            elif starting_time >= datetime.utcnow() and send_email:
                # Alert the operator about the future booking
                tasks.send_email(
                    f"You have a booking of a COVID-19 positive case in your restaurant {restaurant.name}",
                    [operator.email],
                    mail_body_covid_19_operator_booking_alert.format(
                        operator.firstname,
                        restaurant.name,
                        user_booking["id"],
                        table["name"],
                    ),
                )

    return contacts
