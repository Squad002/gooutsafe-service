from flask import Blueprint, redirect, render_template, flash, current_app
from monolith import api
from monolith.services.forms import AuthorityForm

authorities = Blueprint("authorities", __name__)


@authorities.route("/register/authority", methods=["GET", "POST"])
def create_authority():
    form = AuthorityForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Trying to register new authority {form.email.data}")

        authority = api.get_authority_by_email(form.email.data)
        if authority:
            current_app.logger.debug("The authority already exists!")
            return redirect("/login/authority")
        else:
            new_authority = dict(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                phonenumber=str(form.phonenumber.data),
                country=form.country.data,
                state=form.state.data,
                city=form.city.data,
                lat=form.lat.data,
                lon=form.lon.data,
            )

            registered = api.register_authority(new_authority)
            if registered:
                flash(
                    "You are now successfully registered. GoOutSafe!",
                    category="success",
                )
                current_app.logger.info(
                    f"Going to call api to register new authority {form.email.data}"
                )
            else:
                flash("An error occurred with our server.", category="error")
                current_app.logger.error(
                    f"Could not register new authority {form.email.data}"
                )

            return redirect("/")

    return render_template("create_health_authority.html", form=form)
