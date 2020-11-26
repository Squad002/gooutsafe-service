from flask import Blueprint, render_template
from monolith import api

import os

home = Blueprint("home", __name__)


@home.route("/")
def index():
    restaurants = api.get_restaurants()
    for el in restaurants:
        # print(el)
        path = "./monolith/static/uploads/" + str(el["id"])
        photos_paths = os.listdir(path)
        # gets only the first one
        if photos_paths:
            el["path"] = os.path.basename(photos_paths[0])

    restaurants_list = restaurants

    return render_template(
        "index.html",
        restaurants=restaurants,
        restaurants_list=restaurants_list,
    )
