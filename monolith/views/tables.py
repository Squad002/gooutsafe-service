from logging import fatal
from flask.globals import session
from flask.helpers import flash
from flask import Blueprint, redirect, render_template, request, url_for, abort
from flask_login import current_user
from flask_login import login_required
from monolith.services.auth import operator_required, user_required
from monolith.api.tables import register_table, tables_list, patch_table, remove_table
from monolith.api.restaurants import permissions
from monolith.services.forms import CreateTableForm
import flask


#tables = Blueprint("tables", __name__)


""" @tables.route("/restaurants/<restaurant_id>/tables", methods=["GET", "POST"])
@login_required
@operator_required
def _tables(restaurant_id):
    status = permissions(current_user.id, restaurant_id)
    
    if status != 204:
        abort(status)
    alltables = tables_list(restaurant_id)

    return (
        render_template(
            "tables.html",
            tables=alltables,
            base_url=request.base_url,
        ),
        status,
    ) """


@tables.route("/restaurants/<restaurant_id>/tables/new", methods=["GET", "POST"])
@login_required
@operator_required
def create_table(restaurant_id):
    form = CreateTableForm()

    status = permissions(current_user.id, restaurant_id)

    if status != 204:
        abort(status)
        
    if request.method == "POST":
        if form.validate_on_submit():
            new_table = {
                "name" : form.name.data,
                "seats" : form.seats.data,
                "restaurant_id" : int(restaurant_id)
            }

            status = register_table(new_table)
            if status == 201:
                return redirect("/restaurants/" + restaurant_id + "/tables")
            else:
                flash("Table already added", category="error")
        else:
            status = 400

    return render_template("create_table.html", form=form), status

@tables.route(
    "/restaurants/<restaurant_id>/tables/edit/<table_id>",
    methods=["GET", "POST"],
)
@login_required
@operator_required
def edit_table(restaurant_id, table_id):
    status = permissions(current_user.id, restaurant_id)

    if status != 204:
        abort(status)
    form = CreateTableForm()

    if request.method == "POST":
        if form.validate_on_submit():
            table ={
                "name" : form.name.data,
                "seats" : form.seats.data
            }

            status = patch_table(table, int(table_id))
            if status == 204:
                return redirect("/restaurants/" + restaurant_id + "/tables")
            elif status == 400:
                flash(
                    "There is already a table with the same name!",
                    category="error",
                )
            else:
                flash(
                    "Table not found",
                    category="error"
                )
        else:
            status = 400

    return render_template("create_table.html", form=form), status


@tables.route(
    "/restaurants/<restaurant_id>/tables/delete/<table_id>",
    methods=["GET", "POST"],
)
@login_required
@operator_required
def delete_table(restaurant_id, table_id):
    status = permissions(current_user.id, restaurant_id)

    if status != 204:
        abort(status)

    status = remove_table(table_id)

    if status == 204:
        return redirect("/restaurants/" + restaurant_id + "/tables"), status
    else:
        flash("The table to be deleted does not exist!", category="error")

    return redirect("/restaurants/" + restaurant_id + "/tables"), status

