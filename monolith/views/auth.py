from monolith.models.login_user import LoginUser
from flask import Blueprint, render_template, redirect, session, flash, current_app
from flask_login import current_user, login_user, logout_user
from datetime import date


from monolith import db
from monolith.models import User, Operator, HealthAuthority
from monolith.services.forms import LoginForm
from monolith import api

auth = Blueprint("auth", __name__)


@auth.route("/login/user", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        current_app.logger.debug(f"{email} is trying to log-in as an User.")

        if api.login_user(email, password):
            user_data = api.get_user_by_email(email)
            user = LoginUser(user_data)

            logged = login_user(user, force=False)
            if not logged:
                flash("The login was not successfull", category="error")
            else:
                session["role"] = "user"
                session["name"] = user.firstname

                current_app.logger.info(f"{email} successfully logged in.")

            return redirect("/")

    return render_template("login.html", form=form, title="User Login")


@auth.route("/login/operator", methods=["GET", "POST"])
def operator_login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        current_app.logger.debug(f"{email} is trying to log-in as an Operator.")

        if api.login_operator(email, password):
            operator_data = api.get_operator_by_email(email)
            operator = LoginUser(operator_data)

            logged = login_user(operator, force=False)
            if not logged:
                flash("The login was not successfull", category="error")
            else:
                session["role"] = "operator"
                session["name"] = operator.firstname

                current_app.logger.info(f"{email} successfully logged in.")

            return redirect("/")

    return render_template("login.html", form=form, title="Operator Login")


@auth.route("/login/authority", methods=["GET", "POST"])
def authority_login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        current_app.logger.info(f"{email} is trying to log-in.")

        if api.login_authority(email, password):
            authority_data = api.get_authority_by_email(email)
            authority = LoginUser(authority_data)
            login_user(authority)
            session["role"] = "authority"
            session["name"] = authority.name

            current_app.logger.info(f"{email} successfully logged in.")
            return redirect("/")

    return render_template("login.html", form=form, title="Authority Login")


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/")


@auth.route("/unsubscribe")
def unsubscribe():
    if current_user is None or not session.get("role"):
        return redirect("/login/user")

    deleted = False

    if session["role"] == "user":
        user = api.get_user_by_email(current_user.email)
        
        if user["marked"]:
            flash("Positive users cannot be deleted", category="info")
            return redirect("/")

        deleted = api.delete_user(user["id"])
    elif session["role"] == "operator":
        operator = (
            db.session.query(Operator)
            .filter(Operator.email == current_user.email)
            .first()
        )
        operator = api.get_user_by_email(current_user.email)
        deleted = api.delete_operator(operator["id"])
        # TODO add delete of the restaurants or archive them.

    if deleted:
        current_app.logger.info("The user {} deleted him from the app.")
        flash("Your account has been deleted. We will miss you.", category="success")
    else:
        flash("An error occurred with our server", category="error")

    logout_user()
    return redirect("/")
