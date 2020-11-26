from flask import current_app
from flask.globals import session
from flask.helpers import flash
from flask_login import current_user, login_required
from flask import Blueprint, redirect, render_template, request, url_for, abort
from monolith.services.auth import (
    operator_required,
    user_required,
)
from monolith import api
from monolith.services.forms import (
    CreateRestaurantForm,
    CreateTableForm,
    ReviewForm,
    CreateBookingDateHourForm,
    ConfirmBookingForm,
    ChooseReservationData,
)
from datetime import date, timedelta
from werkzeug.utils import secure_filename
from monolith import api

import os
import imghdr
import logging

restaurants = Blueprint("restaurants", __name__)


logger = logging.getLogger("monolith")


@restaurants.route("/restaurants")
def _restaurants(message=""):
    session.pop("previous_search", "")

    if request.args.get("q"):
        query = request.args.get("q")
        session["previous_search"] = query
        allrestaurants = api.get_restaurants_elastic(query=query)
        logger.info(f"Searching for {query}")
    else:        
        allrestaurants = api.get_restaurants()
        
    for el in allrestaurants:
        # print(el)
        path = "./monolith/static/uploads/" + str(el["id"])
        photos_paths = os.listdir(path)
        # gets only the first one
        if photos_paths:
            el["path"] = os.path.basename(photos_paths[0])
    
    return render_template(
        "restaurants.html",
        message=message,
        restaurants=allrestaurants,
        base_url=request.base_url,
        operator_restaurants=False,
    )


@restaurants.route("/restaurants/mine")
@login_required
@operator_required
def operator_restaurants(message=""):
    operator_restaurants = api.operator_restaurants_list(current_user.id)
    return render_template(
        "restaurants.html",
        message=message,
        restaurants=operator_restaurants,
        role=session["role"],
        base_url=request.base_url,
        operator_restaurants=True,
    )


@restaurants.route("/restaurants/map")
def restaurant_map():
    pass



@restaurants.route("/restaurants/<restaurant_id>", methods=["GET", "POST"])
def restaurant_sheet(restaurant_id):
    restaurant = api.get_restaurant_by_id(restaurant_id)

    if restaurant is None:
        abort(404)

    average_rating = round(restaurant["average_rating"], 1)

    # REVIEWS
    # TODO sort them by the most recent, or are they already in that order
    # TODO show in the view the date of the review
    reviews = restaurant["reviews"]
    form = ReviewForm()
    for review in reviews:
        user = api.get_user_by_id(review["user_id"])
        if user:
            review["name"] = user["firstname"]
            review["avatar_link"] = current_app.config["AVATAR_PROVIDER"].format(seed=user["avatar_id"])
            review["created"] = review["created"][0:10]
                
    if form.is_submitted():
        if current_user.is_anonymous:
            flash("To review the restaurant you need to login.")
            return redirect(url_for("auth.login"))
        if form.validate():
            if session["role"] != "user":
                flash("Only a logged user can review a restaurant.")
            else:
                review = {
                    "message": form.message.data,
                    "rating": form.rating.data,
                    "user_id": current_user.id,
                    "restaurant_id": int(restaurant_id)
                }
                status = api.register_review(review)
                # Check if the user already did a review
                if status == 409:
                    flash("You already reviewed this restaraunt")
                else:
                    return redirect("/restaurants/" + restaurant_id)

    path = "./monolith/static/uploads/" + str(restaurant_id)
    photos_paths = os.listdir(path)

    names = []
    for path in photos_paths:
        names.append(os.path.basename(path))

    return render_template(
        "restaurantsheet.html",
        id=restaurant["id"],
        name=restaurant["name"],
        lat=restaurant["lat"],
        lon=restaurant["lon"],
        phonenumber=restaurant["phone"],
        precautions=restaurant["precautions"],
        average_rating=restaurant["average_rating"],
        open=restaurant["opening_hours"],
        close=restaurant["closing_hours"],
        cuisine=restaurant["cuisine_type"],
        menus=restaurant["menus"],
        base_url=request.base_url,
        reviews=reviews,
        form=form,
        operator_id=restaurant["operator_id"],
        file_names=names
    )


@restaurants.route("/restaurants/<restaurant_id>/booking", methods=["GET", "POST"])
@login_required
@user_required
def book_table_form(restaurant_id):
    if current_user.marked == True:
        flash("You are marked so you can't book a table")
        return redirect("/restaurants/" + str(restaurant_id))

    form = CreateBookingDateHourForm()
    max_table_seats = api.max_table_seats(restaurant_id)  # Take max seats from tables of restaurant_id
    restaurant = api.get_restaurant_by_id(restaurant_id)
    time = []
    range_hour = restaurant["time_of_stay"]
    opening_hour = restaurant["opening_hours"] * 60
    closing_hour = restaurant["closing_hours"]* 60
    
    if closing_hour < opening_hour:
        closing_hour = closing_hour + (24 * 60)
    
    for i in range(opening_hour, closing_hour, range_hour):
        time.append(
            str(timedelta(minutes=i))[:-3]
            + " - "
            + str(timedelta(minutes=i + range_hour))[:-3]
        )

    if request.method == "POST":
        if form.validate_on_submit():
            seats = int(request.form["number_persons"])
            booking_hour_start = request.form["booking_hour"].split(" - ")[0]
            booking_hour_end = request.form["booking_hour"].split(" - ")[1]
            booking_date = request.form["booking_date"]
            booking_date_start = booking_date + " " + booking_hour_start
            booking_date_end = booking_date + " " + booking_hour_end

            confirmed_bookign = True if seats == 1 else False
            booking = api.make_booking(
                confirmed_bookign,
                booking_date_end,
                restaurant["id"],
                seats,
                booking_date_start,
                current_user.id,
            )

            if booking.status_code == 404:  
                flash(
                    "No tables avaible for "
                    + str(seats)
                    + " people for this date and time"
                ) 

            else:
                if confirmed_bookign:
                    flash("Booking confirmed", category="success")
                    return redirect("/restaurants")
                else:
                    session["booking_number"] = booking.json()
                    session["seats"] = seats
                    return redirect(
                        url_for(".confirm_booking",
                                restaurant_id=restaurant_id)
                    )
        else:
            flash("Are you really able to go back to the past?")

    return render_template(
        "book_table.html", form=form, max_table_seats=max_table_seats, hours_list=time
    )


@restaurants.route(
    "/restaurants/<restaurant_id>/booking/confirm", methods=["GET", "POST"]
)
@login_required
@user_required
def confirm_booking(restaurant_id):
    booking_number = session["booking_number"]
    seats = session["seats"]
    form = ConfirmBookingForm(seats - 1)
    error = False

    if form.validate_on_submit():
        booking = api.get_booking_by_id(booking_number)

        users_list_booking = {
            "booking_number": booking_number,
            "users": []
        }
        users_list = users_list_booking["users"]
        for i, field in enumerate(form.people):
            user = {
                "firstname": field.firstname.data,
                "lastname": field.lastname.data,
                "email": field.email.data,
                "fiscalcode": field.fiscalcode.data,
            }

            users_list.append(user)

        res = api.confirm_booking(users_list_booking)

        if res.status_code != 201:
            flash(res.json())
        else:
            session.pop("booking_number", None)
            session.pop("seats", None)
            flash("Booking confirmed", category="success")

            send_booking_confirmation_mail(booking_number)
            return redirect("/restaurants")


    return render_template(
        "confirm_booking.html", form=form, number_persons=int(seats)
    )


def send_booking_confirmation_mail(booking_number):
    pass
    # bookings = api.get_booking_by_id(booking_number)
    # first_user = None

    # for i in range(0, len(bookings)):
    #     booking = bookings[i]
    #     user = booking["user_id"]
    #     booking_date = booking["start_booking"].strftime("%d %b %Y, %H:%M")
    #     restaurant = booking.table.restaurant.name
    #     restaurant = api.get_r

    #     if i == 0:
    #         first_user = user
    #         # Send mail to the person that booked
    #         mail_message = f"Hey {user.firstname}!\nThe booking at {restaurant} in date {booking_date} is confirmed.\nHave a safe meal!\n\nThe team of GoOutSafe"
    #     else:
    #         # Send mail to the people that have been booked by the first person
    #         mail_message = f"Hey {user.firstname}!\nYour friend {first_user.firstname} booked at {restaurant} in date {booking_date}.\nHave a safe meal!\n\nThe team of GoOutSafe"

    #     # TODO CALL celery one day
    #     # send_email(
    #     #     f"Booking at {restaurant} has been confirmed!",
    #     #     [user.email],
    #     #     mail_message,
    #     #     mail_message,
    #     # )


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + format


@restaurants.route('/restaurants/<restaurant_id>/upload', methods=['GET', 'POST'])
@login_required
@operator_required
def handle_upload(restaurant_id):
    restaurant = api.get_restaurant_by_id(int(restaurant_id))

    if restaurant is None:
        abort(404)

    if request.method == "POST":
        for key, uploaded_file in request.files.items():
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in [".png", ".jpg", ".jpeg"] or \
                    file_ext != validate_image(uploaded_file.stream):
                    return '', 400
                uploaded_file.save(os.path.join("./monolith/static/uploads/" + str(restaurant_id), filename))
        
        return redirect("/restaurants/mine")

    return render_template("upload_photos.html", id=restaurant_id)


@restaurants.route("/restaurants/new", methods=["POST", "GET"])
@login_required
@operator_required
def create_restaurant():
    status = 200
    form = CreateRestaurantForm()
    if request.method == "POST":
        if form.validate_on_submit():
            precautions = [v for k, v in form.prec_measures.data]
            new_restaurant = {
                "closing_hours": form.closing_hours.data,
                "cuisine_type": form.cuisine_type.data,
                "lat": form.lat.data,
                "lon": form.lon.data,
                "name": form.name.data,
                "opening_hours": form.opening_hours.data,
                "operator_id": current_user.id,
                "phone": str(form.phonenumber.data),
                "precautions": precautions,
                "time_of_stay": int(form.time_of_stay.data)
            }

            status = api.register_restaurant(new_restaurant)
            if status == 201:
                return redirect("/restaurants/mine")
            else:
                flash("Restaurant already added", category="error")
        else:
            status = 400

    return render_template("create_restaurant.html", form=form), status


@restaurants.route("/restaurants/<restaurant_id>/menus/new", methods=["GET", "POST"])
@login_required
@operator_required
def create_menu(restaurant_id):
    status = 200
    
    zipped = None
    menu_name = ""

    res = api.get_restaurant_by_id(restaurant_id)

    if res == None:
        abort(404)

    if res["operator_id"] != current_user.id:
        abort(403)
    
    choices = [
            "PIZZAS",
            "STARTERS",
            "DRINKS",
            "MAIN_COURSES"
            "SIDE_DISHES",
            "DESSERTS",
            "BURGERS",
            "SANDWICHES"
        ]
    values = [
        "Pizzas",
        "Starters",
        "Main courses"
        "Side dishes",
        "Drinks",
        "Sandwiches",
        "Burgers",
        "Desserts"
    ]

    if request.method == "POST":
        menu_name = request.form["menu_name"]
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
                elif food["name"] in food_names:
                    flash("No duplicate foods", category="error")
                    status = 400
                else:
                    menu["foods"].append(food)
                    food_names.add(food["name"])
                    status = 200

            if status == 200:
                status = api.register_menu(menu)
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
        print("primo render")
        return (
            render_template(
                "create_menu.html",
                choices=choices,
                values=values,
                items=zip_to_send,
                menu_name=menu_name,
            ),
            status,
        )
    else:
        print("secondo render")
        return (
            render_template("create_menu.html",
                            choices=choices,
                            values=values),
            status,
        )


@restaurants.route(
    "/restaurants/<restaurant_id>/menus/show/<menu_id>", methods=["GET", "POST"]
)
def show_menu(restaurant_id, menu_id):
    menu = api.menu_sheet(menu_id)

    if menu is None:
        abort(404)

    return render_template("show_menu.html", menu=menu)


@restaurants.route("/restaurants/<restaurant_id>/tables")
@login_required
@operator_required
def _tables(restaurant_id):
    res = api.get_restaurant_by_id(restaurant_id)
    status = 200
    if res == None:
        abort(404)

    if res["operator_id"] != current_user.id:
        abort(403)    

    alltables = api.tables_list(restaurant_id)

    print(alltables)
    return (
        render_template(
            "tables.html",
            tables=alltables,
            base_url=request.base_url,
        ),
        status,
    ) 


@restaurants.route("/restaurants/<restaurant_id>/tables/new", methods=["GET", "POST"])
@login_required
@operator_required
def create_table(restaurant_id):
    status = 200
    form = CreateTableForm()
    res = api.get_restaurant_by_id(restaurant_id)

    if res == None:
        abort(404)

    if res["operator_id"] != current_user.id:
        abort(403)
        
    if request.method == "POST":
        if form.validate_on_submit():
            new_table = {
                "name" : form.name.data,
                "seats" : form.seats.data,
                "restaurant_id" : int(restaurant_id)
            }

            status = api.register_table(new_table)
            if status == 201:
                return redirect("/restaurants/" + restaurant_id + "/tables")
            else:
                flash("Table already added", category="error")
        else:
            status = 400

    return render_template("create_table.html", form=form), status


@restaurants.route(
    "/restaurants/<restaurant_id>/tables/edit/<table_id>",
    methods=["GET", "POST"],
)
@login_required
@operator_required
def edit_table(restaurant_id, table_id):
    res = api.get_restaurant_by_id(restaurant_id)
    status = 200
    if res == None:
        abort(404)

    if res["operator_id"] != current_user.id:
        abort(403)
    form = CreateTableForm()

    status = 200
    if request.method == "POST":
        if form.validate_on_submit():
            table ={
                "name" : form.name.data,
                "seats" : form.seats.data
            }

            status = api.patch_table(table, int(table_id))
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


@restaurants.route(
    "/restaurants/<restaurant_id>/tables/delete/<table_id>",
    methods=["GET", "POST"],
)
@login_required
@operator_required
def delete_table(restaurant_id, table_id):
    res = api.get_restaurant_by_id(restaurant_id)

    if res == None:
        abort(404)

    if res["operator_id"] != current_user.id:
        abort(403)

    status = api.remove_table(table_id)

    if status == 204:
        return redirect("/restaurants/" + restaurant_id + "/tables"), status
    else:
        flash("The table to be deleted does not exist!", category="error")

    return redirect("/restaurants/" + restaurant_id + "/tables"), status


@restaurants.route("/restaurants/<restaurant_id>/reservations", methods=["GET", "POST"])
@login_required
@operator_required
def operator_reservations_list(restaurant_id):
    operator = api.get_restaurant_by_id(restaurant_id)

    if operator["operator_id"] != current_user.id:
        flash("Access denied")
        return redirect("/restaurants")

    form = ChooseReservationData()
    date_show = date.today()

    booking_list = api.reservations_list_by_restaurant_id_date(restaurant_id, str(date_show))

    if request.method == "POST":
        if form.validate_on_submit():
            chosen_date = request.form["date"]
            date_show = request.form["date"]

            booking_list = api.reservations_list_by_restaurant_id_date(restaurant_id, chosen_date)

    total_people = 0
    for booking in booking_list:
        total_people += booking["people_number"]

    return render_template(
        "reservations.html",
        form=form,
        booking_list=booking_list,
        date=date_show,
        total_people=total_people,
        base_url=request.base_url,
    )


@restaurants.route(
    "/restaurants/<restaurant_id>/reservations/<booking_number>",
    methods=["GET", "POST"],
)
@operator_required
@login_required
def operator_checkin_reservation(restaurant_id, booking_number):
    
    if api.check_permission(booking_number, current_user.id, restaurant_id) == False:  # check if operator can see the page
        flash("Operation denied ")
        return redirect(
            url_for(".operator_reservations_list", restaurant_id=restaurant_id)
        )

    if request.method == "POST":
        checkin = {
            "booking_number": int(booking_number),
            "user_list": []
        }
        user_list = checkin["user_list"]
        for user_id in request.form.getlist("people"):
            user_list.append({"user_id": int(user_id)})
        
        api.confirm_checkin(checkin)


    confirmed_booking_checkin_done = api.booking_and_checkin(booking_number)

    confirmed_booking = confirmed_booking_checkin_done["confirmed_booking"]
    checkin_done = confirmed_booking_checkin_done["checkin"]

    user_list = api.get_users_reservation(booking_number)

    user_list_with_marks = []
    someone_marked = False

    for user in user_list:
        if user["marked"]:
            someone_marked = True
        user_list_with_marks.append((user, user["marked"]))

    if someone_marked:
        flash("Attentions, people in red are marked as covid positive")
    return render_template(
        "reservation.html",
        user_list=user_list_with_marks,
        confirmed_booking=confirmed_booking,
        checkin=checkin_done,
    )


@restaurants.route(
    "/restaurants/<restaurant_id>/reservations/delete/<booking_number>",
    methods=["GET", "POST"],
)
@operator_required
@login_required
def operator_delete_reservation(restaurant_id, booking_number):

    if api.check_permission(booking_number, current_user.id, restaurant_id) == False:  # check if operator can see the page
        flash("Operation denied")
        return redirect(
            url_for(".operator_reservations_list", restaurant_id=restaurant_id)
        )

    api.delete_reservation(booking_number)

    flash("Reservation deleted", category="success")
    return redirect(url_for(".operator_reservations_list", restaurant_id=restaurant_id))


@restaurants.route("/bookings", methods=["GET", "POST"])
@login_required
@user_required
def user_booking_list():
    list_booking_with_restaurant = api.user_booking_list(current_user.id)

    return render_template(
            "user_list_bookings.html",
            list_booking=list_booking_with_restaurant,
            base_url=request.base_url,
            go_back="/"
    )


@restaurants.route("/bookings/delete/<booking_number>", methods=["GET", "POST"])
@login_required
@user_required
def user_delete_booking(booking_number):
    booking = api.get_booking_by_id(booking_number)
    if not booking or booking["user_id"] != current_user.id:
        flash("Operation denied")
        return redirect(url_for('.user_booking_list'))

    api.delete_booking(current_user.id, booking_number)

    flash('Booking deleted', category='success')
    return redirect(url_for('.user_booking_list'))