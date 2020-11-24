from flask import Blueprint, redirect, render_template, current_app, flash
from monolith import api
from monolith.services.forms import OperatorForm
from datetime import datetime

operators = Blueprint("operators", __name__)


@operators.route("/register/operator", methods=["GET", "POST"])
def create_operator():
    form = OperatorForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Trying to register new operator {form.email.data}")

        operator = api.get_operator_by_email(form.email.data)
        if operator:
            current_app.logger.debug("The operator already exists!")
            return redirect("/login/operator")
        else:
            new_operator = dict(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                email=form.email.data,
                password=form.password.data,
                birthdate=datetime.strftime(form.dateofbirth.data, "%Y-%m-%d"),
                phonenumber=str(form.phonenumber.data),
                fiscalcode=form.fiscalcode.data,
            )

            registered = api.register_operator(new_operator)
            if registered:
                flash(
                    "You are now successfully registered. GoOutSafe!",
                    category="success",
                )
                current_app.logger.info(
                    f"Going to call api to register new operator {form.email.data}"
                )
            else:
                flash("An error occurred with our server.", category="error")
                current_app.logger.error(
                    f"Could not register new operator {form.email.data}"
                )

            return redirect("/")

    return render_template("create_operator.html", form=form)