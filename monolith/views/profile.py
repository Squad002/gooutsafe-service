from monolith import api
from flask import Blueprint, render_template, session, redirect
from flask_login import login_required
from flask.helpers import flash


from monolith.services.auth import current_user
from monolith.services.forms import (
    ChangePasswordForm,
    ChangeAnagraphicForm,
    ChangeContactForm,
)

me = Blueprint("me", __name__)



@me.route("/me")
@login_required
def profile():
    if session["role"] == "authority":
        return redirect("/")
    elif session["role"] == "user":
        user = api.get_user_by_id(current_user.id)
        return render_template("profile.html", user=user)
    elif session["role"] == "operator":
        user = api.get_operator_by_id(current_user.id)
        return render_template("profile.html", user=user)


@me.route("/me/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if api.login_user(current_user.email, form.old_password.data):
            if form.password_confirm.data == form.new_password.data:
                api.patch_user(current_user.id, {"password": form.new_password.data})
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
            if api.login_operator(current_user.email, form.password.data):
                # TODO add patch for birthdate to user service api
                res = api.patch_operator(
                    current_user.id,
                    {
                        "firstname": form.firstname.data,
                        "lastname": form.lastname.data,
                        "fiscalcode": form.fiscalcode.data,
                    },
                )
                flash("Operation successful!")
            else:
                flash("You've typed the wrong password!")
        if session["role"] == "user":
            if api.login_user(current_user.email, form.password.data):
                # TODO add patch for birthdate to user service api
                res = api.patch_user(
                    current_user.id,
                    {
                        "firstname": form.firstname.data,
                        "lastname": form.lastname.data,
                        "fiscalcode": form.fiscalcode.data,
                    },
                )
                flash("Operation successful!")
            else:
                flash("You've typed the wrong password!")

    return render_template("change_profile.html", form=form)


@me.route("/me/change_contacts", methods=["GET", "POST"])
@login_required
def change_contacts():
    form = ChangeContactForm()

    if form.validate_on_submit():
        if api.login_user(current_user.email, form.password.data):
            api.patch_user(
                current_user.id,
                {"email": form.email.data, "phonenumber": str(form.phonenumber.data)},
            )
            flash("Operation successful!")
        else:
            flash("You've typed the wrong password!")
    return render_template("change_profile.html", form=form)
