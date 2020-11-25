from flask.globals import session
from flask.helpers import flash
from flask import Blueprint, redirect, render_template, request, url_for, abort
from flask_login import current_user
from flask_login import login_required
from monolith.services.auth import operator_required, user_required
from monolith.api.menus import register_menu
from monolith.api.restaurants import permissions

menus = Blueprint("menus", __name__)


@menus.route("/restaurants/<restaurant_id>/menus/new", methods=["GET", "POST"])
@login_required
@operator_required
def create_menu(restaurant_id):
    status = 200
    
    zipped = None
    menu_name = ""
    status = permissions(operator_id, restaurant_id)
    if status == 403:
        abort(403)
        
    if request.method == "POST":
        menu_name = request.form["menu_name"]

        choices = [
            "ETHNIC",
            "PUB",
            "FAST_FOOD"
        ]
        values = [
            "Ethnic",
            "Pub",
            "Fast Food"
        ]

        if menu_name == "":
            flash("No empty menu name!", category="error")
            status = 400
        else:
            menu = {
                "name" : menu_name,
                "foods" : [],
                "restaurant_id" : int(restaurant_id)
            }

            food_names = set()
            zipped = zip(
                request.form.getlist("name"),
                request.form.getlist("price"),
                request.form.getlist("category"),
            )
            for name, price, category in zipped:
                food = {
                    "name" : name,
                    "category" : category,
                    "price" : price
                }
                try:
                    food["price"] = float(price)
                    is_float = True
                except ValueError:
                    is_float = False

                if not is_float:
                    flash("Not a valid price number", category="error")
                    status = 400
                elif food["price"] < 0:
                    flash("No negative values!", category="error")
                    status = 400
                elif food["name"] == "":
                    flash("No empty food name!", category="error")
                    status = 400
                elif food["category"] not in choices:
                    flash("Wrong category selected!", category="error")
                    status = 400
                elif food["names"] in food_names:
                    flash("No duplicate food name!", category="error")
                    status = 400
                else:
                    menu.foods.append(food)
                    food_names.add(food.name)

                if status == 200:
                    status = register_menu(menu)

                    if status == 201:
                        return redirect("/restaurants/" + str(restaurant_id))
                    else:
                        flash("A menu with the same name already exists")

    if zipped or menu_name:
        zip_to_send = zip(
            request.form.getlist("name"),
            request.form.getlist("price"),
            request.form.getlist("category"),
        )

        return (
            render_template(
                "create_menu.html",
                choices=choices,
                values=values,
                items=zip_to_send,
                menu_name=name,
            ),
            status,
        )
    else:
        return (
            render_template("create_menu.html",
                            choices=choices,
                            values=values),
            status,
        )