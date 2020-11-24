from monolith.api.operators import patch_operator
from requests.api import request
from monolith.api.users import login_user, patch_user
from monolith.api.operators import login_operator, patch_operator
from flask import Blueprint, render_template, session, redirect
from flask_login import login_required
from flask.helpers import flash
from datetime import datetime


from monolith import db
from monolith.models import User, Operator
from monolith.services.auth import current_user
from monolith.services.forms import (
    ChangePasswordForm,
    ChangeAnagraphicForm,
    ChangeContactForm,
)

me = Blueprint("me", __name__)

from monolith.services.api import get_operator_by_id, get_user_by_id


@me.route("/me")
@login_required
def profile():
    if session["role"] == "authority":
        return redirect("/")
    elif session["role"] == "user":
        user = get_user_by_id(current_user.id)
        return render_template("profile.html", user=user)
    elif session["role"] == "operator":
        user = get_operator_by_id(current_user.id)
        return render_template("profile.html", user=user)


@me.route("/me/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if login_user(current_user.email, form.old_password.data):
            if(form.password_confirm.data == form.new_password.data):
                patch_user(current_user.id, {"password": form.new_password.data})
                flash("Operation successful!")
        else:
            flash("You've typed the wrong password!")

    return render_template("change_profile.html", form=form)


@me.route("/me/change_anagraphic", methods=["GET", "POST"])
@login_required
def change_anagraphic():
    form = ChangeAnagraphicForm()

    if form.validate_on_submit():
        if session["role"] == "operator":
            if login_operator(current_user.email, form.password.data):
                # TODO add patch for birthdate to user service api
                res = patch_operator(current_user.id, {"firstname": form.firstname.data, "lastname": form.lastname.data, "fiscalcode": form.fiscalcode.data})
                flash("Operation successful!")
            else:
                flash("You've typed the wrong password!")
        if session["role"] == "user":
            if login_user(current_user.email, form.password.data):
                # TODO add patch for birthdate to user service api
                res = patch_user(current_user.id, {"firstname": form.firstname.data, "lastname": form.lastname.data, "fiscalcode": form.fiscalcode.data})
                flash("Operation successful!")
            else:
                flash("You've typed the wrong password!")

    return render_template("change_profile.html", form=form)


@me.route("/me/change_contacts", methods=["GET", "POST"])
@login_required
def change_contacts():
    form = ChangeContactForm()

    if form.validate_on_submit():
        if login_user(current_user.email, form.password.data):
            patch_user(current_user.id, {'email': form.email.data, 'phonenumber' : str(form.phonenumber.data)})
            flash("Operation successful!")
        else:
            flash("You've typed the wrong password!")
    return render_template("change_profile.html", form=form)
