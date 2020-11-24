from flask import Blueprint, redirect, render_template, current_app, flash
from monolith import db, redis_client
from monolith.models import User
from monolith.services.forms import UserForm
from monolith.services.auth import authority_required
from monolith.services.breakers import read_request_breaker
from monolith.services.api import get_users  # todo rmiuover
from monolith import api

from datetime import datetime

users = Blueprint("users", __name__)


@users.route("/users")
@authority_required
def _users():
    users = get_users()

    # except requests.exceptions.Timeout as timeout:
    #     current_app.logger.warning(timeout)
    #     flash("The request timed out. Retry later", category="error")
    # except requests.exceptions.RequestException as e:
    #     flash("An unexpected error occurred. Retry later", category="error")
    #     current_app.logger.error(e)

    return render_template("users.html", users=users)


@users.route("/register/user", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Trying to register new user {form.email.data}")

        user = api.get_user_by_email(form.email.data)
        if user:
            current_app.logger.debug("The user already exists!")
            return redirect("/login/user")
        else:
            new_user = dict(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                email=form.email.data,
                password=form.password.data,
                birthdate=datetime.strftime(form.dateofbirth.data, "%Y-%m-%d"),
                phonenumber=str(form.phonenumber.data),
                fiscalcode=form.fiscalcode.data,
            )

            registered = api.register_user(new_user)
            if registered:
                flash(
                    "You are now successfully registered. GoOutSafe!",
                    category="success",
                )
                current_app.logger.info(
                    f"Going to call api to register new user {form.email.data}"
                )
            else:
                flash("An error occurred with our server.", category="error")
                current_app.logger.error(
                    f"Could not register new user {form.email.data}"
                )

            return redirect("/")

    return render_template("create_user.html", form=form)
