from sqlalchemy import or_
from flask import Blueprint, render_template, flash, redirect, request, session
from flask_login.utils import login_required

from monolith import db
from monolith.models import User
from monolith.services.auth import current_user, authority_required
from monolith.services.forms import AuthorityIdentifyForm
from monolith.services.background import tasks
from monolith import api

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
        marked = api.mark(current_authority.id, identifier, form.duration.data)

        if marked:
            flash("User was marked.", category="success")
        else:
            flash("User not found.", category="error")

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

        current_authority = current_user
        contacts = api.trace(current_authority.id, identifier, form.duration.data)

        if not contacts:
            flash("The user was not found", category="error")

    return render_template("trace.html", form=form, contacts=contacts)
