from flask.globals import session
from flask.helpers import flash
from flask import Blueprint, redirect, render_template, request, url_for, abort
from monolith import db
from monolith.models import (
    Restaurant,
    RestaurantsPrecautions,
    Table,
    User,
    Booking,
    Mark,
    Operator,
)
from monolith.models.menu import Menu, Food, FoodCategory
from monolith.models.table import Table
from monolith.api.restaurants import register_restaurant, permissions, operator_restaurants_list
from monolith.services.auth import (
    current_user,
    operator_required,
    user_required,
)
from flask_login import current_user, login_required
from monolith.services.forms import (
    CreateRestaurantForm,
    CreateTableForm,
    ReviewForm,
    CreateBookingDateHourForm,
    ConfirmBookingForm,
    ChooseReservationData,
)
from datetime import date, timedelta, datetime
from sqlalchemy import func
from flask_login import current_user
from monolith.services.background.tasks import send_email
from werkzeug.utils import secure_filename

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
        results, total = Restaurant.search(query, 1, 20)
        allrestaurants = results.all()
        logger.info(f"Searching for {query}")
    else:            
        allrestaurants = db.session.query(Restaurant)

    restaurants = [res.__dict__ for res in allrestaurants]
    images_path_dict = {}
    for el in restaurants:
        # print(el)
        path = "./monolith/static/uploads/" + str(el["id"])
        photos_paths = os.listdir(path)
        # gets only the first one
        if photos_paths:
            el["path"] = os.path.basename(photos_paths[0])
    
    return render_template(
        "restaurants.html",
        message=message,
        restaurants=restaurants,
        paths=images_path_dict,
        base_url=request.base_url,
        operator_restaurants=False,
    )


@restaurants.route("/restaurants/mine")
@login_required
@operator_required
def operator_restaurants(message=""):
    operator_restaurants = operator_restaurants_list(current_user.id)
    return render_template(
        "restaurants.html",
        message=message,
        restaurants=operator_restaurants,
        role=session["role"],
        base_url=request.base_url,
        operator_restaurants=True,
    )


@restaurants.route("/restaurants/<restaurant_id>", methods=["GET", "POST"])
def restaurant_sheet(restaurant_id):
    q_restaurant = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).first()

    if q_restaurant is None:
        abort(404)

    q_restaurant_precautions = (
        db.session.query(Precautions.name)
        .filter(
            Precautions.id == RestaurantsPrecautions.precautions_id,
            RestaurantsPrecautions.restaurant_id == int(restaurant_id),
        )
        .all()
    )

    precautions = []
    for prec in q_restaurant_precautions:
        precautions.append(prec.name)

    average_rating = round(q_restaurant.average_rating, 1)

    # REVIEWS
    # TODO sort them by the most recent, or are they already in that order
    # TODO show in the view the date of the review
    reviews = q_restaurant.reviews
    form = ReviewForm()
    if form.is_submitted():
        if current_user.is_anonymous:
            flash("To review the restaurant you need to login.")
            return redirect(url_for("auth.login"))
        if form.validate():
            if session["role"] != "user":
                flash("Only a logged user can review a restaurant.")
            else:
                # Check if the user already did a review
                if current_user.already_reviewed(q_restaurant):
                    flash("You already reviewed this restaraunt")
                else:
                    rating = form.rating.data
                    message = form.message.data
                    current_user.review(q_restaurant, rating, message)
                    db.session.commit()
                    return redirect("/restaurants/" + restaurant_id)

    path = "./monolith/static/uploads/" + str(restaurant_id)
    photos_paths = os.listdir(path)

    names = []
    for path in photos_paths:
        names.append(os.path.basename(path))

    return render_template(
        "restaurantsheet.html",
        id=q_restaurant.id,
        name=q_restaurant.name,
        lat=q_restaurant.lat,
        lon=q_restaurant.lon,
        phonenumber=q_restaurant.phonenumber,
        precautions=precautions,
        average_rating=average_rating,
        open=q_restaurant.opening_hours,
        close=q_restaurant.closing_hours,
        cuisine=q_restaurant.cuisine_type.value,
        menus=q_restaurant.menus,
        base_url=request.base_url,
        reviews=reviews,
        form=form,
        operator_id=q_restaurant.operator_id,
        file_names=names
    )


@restaurants.route("/restaurants/<restaurant_id>/booking", methods=["GET", "POST"])
@login_required
@user_required
def book_table_form(restaurant_id):
    if db.session.query(Mark).filter_by(user_id=current_user.id).first() is not None:
        flash("You are marked so you can't book a table")
        return redirect("/restaurants/" + str(restaurant_id))

    form = CreateBookingDateHourForm()
    max_table_seats = (
        db.session.query(func.max(Table.seats))
        .filter(Table.restaurant_id == restaurant_id)
        .first()[0]
    )  # Take max seats from tables of restaurant_ud
    time = []
    range_hour = (
        db.session.query(Restaurant.time_of_stay).filter_by(
            id=restaurant_id).first()[0]
    )
    opening_hour = int(
        db.session.query(Restaurant.opening_hours)
        .filter_by(id=restaurant_id)
        .first()[0]
        * 60
    )
    closing_hour = int(
        db.session.query(Restaurant.closing_hours)
        .filter_by(id=restaurant_id)
        .first()[0]
        * 60
    )
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
            number_persons = int(request.form["number_persons"])
            booking_hour_start = request.form["booking_hour"].split(" - ")[0]
            booking_hour_end = request.form["booking_hour"].split(" - ")[1]
            booking_date = request.form["booking_date"]
            booking_date_start = datetime.strptime(
                booking_date + " " + booking_hour_start, "%Y-%m-%d %H:%M"
            )
            booking_date_end = datetime.strptime(
                booking_date + " " + booking_hour_end, "%Y-%m-%d %H:%M"
            )

            restaurant = (
                db.session.query(Restaurant)
                .filter(Restaurant.id == restaurant_id)
                .first()
            )
            table = restaurant.get_free_table(
                number_persons, booking_date_start)

            if table is None:
                flash(
                    "No tables avaible for "
                    + str(number_persons)
                    + " people for this date and time"
                )
            else:
                booking_number = db.session.query(
                    func.max(Booking.booking_number)
                ).first()[0]
                print(booking_number)
                if booking_number is None:
                    booking_number = 1
                else:
                    booking_number += 1

                confirmed_bookign = True if number_persons == 1 else False
                db.session.add(
                    Booking(
                        user_id=current_user.id,
                        table_id=table,
                        booking_number=booking_number,
                        start_booking=booking_date_start,
                        end_booking=booking_date_end,
                        confirmed_booking=confirmed_bookign,
                    )
                )
                db.session.commit()

                old_booking_number = booking_number

                if confirmed_bookign:
                    flash("Booking confirmed", category="success")
                    return redirect("/restaurants")
                else:
                    session["booking_number"] = old_booking_number
                    session["number_persons"] = number_persons
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
    number_persons = session["number_persons"]
    form = ConfirmBookingForm(number_persons - 1)
    error = False

    if form.validate_on_submit():
        booking = (
            db.session.query(Booking).filter_by(
                booking_number=booking_number).first()
        )

        for i, field in enumerate(form.people):
            user = (
                db.session.query(User)
                .filter_by(fiscalcode=field.fiscalcode.data)
                .first()
            )
            if user is None:
                if (
                    db.session.query(User).filter_by(
                        email=field.email.data).first()
                    is None
                ):  # check if email is already in the db or not
                    user = User(
                        firstname=field.firstname.data,
                        lastname=field.lastname.data,
                        email=field.email.data,
                        fiscalcode=field.fiscalcode.data,
                    )
                    db.session.add(user)
                    db.session.commit()
                else:
                    flash(
                        "Person " + str(i + 1) +
                        ", mail already used from another user"
                    )
                    error = True
                    break
            else:
                if not user.check_equality_for_booking(
                    field.firstname.data, field.lastname.data, field.email.data
                ):  # if the user exists, check if the data filled are correct
                    flash("Person " + str(i + 1) + ", incorrect data")
                    error = True
                    break
                if booking.user_already_booked(user.id):
                    flash(
                        "Person "
                        + str(i + 1)
                        + ", user already registered in the booking"
                    )
                    error = True
                    break
            db.session.add(
                Booking(
                    user_id=user.id,
                    table_id=booking.table_id,
                    booking_number=booking.booking_number,
                    start_booking=booking.start_booking,
                    end_booking=booking.end_booking,
                    confirmed_booking=True,
                )
            )

        if error:
            db.session.rollback()
        else:
            booking.confirmed_booking = True
            db.session.commit()

            session.pop("booking_number", None)
            session.pop("number_persons", None)
            flash("Booking confirmed", category="success")

            send_booking_confirmation_mail(booking_number)
            return redirect("/restaurants")

    return render_template(
        "confirm_booking.html", form=form, number_persons=int(number_persons)
    )


def send_booking_confirmation_mail(booking_number):
    bookings = (
        db.session.query(Booking).filter(
            Booking.booking_number == booking_number).all()
    )
    first_user = None

    for i in range(0, len(bookings)):
        booking = bookings[i]
        user = booking.user
        booking_date = booking.start_booking.strftime("%d %b %Y, %H:%M")
        restaurant = booking.table.restaurant.name

        if i == 0:
            first_user = user
            # Send mail to the person that booked
            mail_message = f"Hey {user.firstname}!\nThe booking at {restaurant} in date {booking_date} is confirmed.\nHave a safe meal!\n\nThe team of GoOutSafe"
        else:
            # Send mail to the people that have been booked by the first person
            mail_message = f"Hey {user.firstname}!\nYour friend {first_user.firstname} booked at {restaurant} in date {booking_date}.\nHave a safe meal!\n\nThe team of GoOutSafe"

        send_email(
            f"Booking at {restaurant} has been confirmed!",
            [user.email],
            mail_message,
            mail_message,
        )


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
    q_restaurant = db.session.query(Restaurant).filter_by(
        id=int(restaurant_id)).first()

    if q_restaurant is None:
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
            precautions = [v for k, v in form.precautions]
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

            status = register_restaurant(new_restaurant)
            if status == 201:
                return redirect("/restaurants/mine")
            else:
                flash("Restaurant already added", category="error")
        else:
            status = 400

    return render_template("create_restaurant.html", form=form), status


@restaurants.route("/restaurants/<restaurant_id>/reservations", methods=["GET", "POST"])
@login_required
@operator_required
def operator_reservations_list(restaurant_id):
    operator_id = (
        db.session.query(Restaurant.operator_id).filter_by(
            id=restaurant_id).first()[0]
    )

    if operator_id != current_user.id:
        flash("Access denied")
        return redirect("/restaurants")

    form = ChooseReservationData()
    date_show = date.today()
    tomorrow = date_show + timedelta(days=1)

    booking_list = (
        db.session.query(Booking, Table, func.count())
        .join(Table)
        .join(Restaurant)
        .filter(
            Restaurant.id == restaurant_id,
            Booking.start_booking >= date.today(),
            Booking.start_booking < tomorrow,
        )
        .group_by(Booking.booking_number)
        .order_by(Booking.start_booking.asc())
        .all()
    )

    if request.method == "POST":
        if form.validate_on_submit():
            chosen_date = datetime.strptime(request.form["date"], "%Y-%m-%d")
            tomorrow = chosen_date + timedelta(days=1)
            date_show = request.form["date"]

            booking_list = (
                db.session.query(Booking, Table, func.count())
                .join(Table)
                .join(Restaurant)
                .filter(
                    Restaurant.id == restaurant_id,
                    Booking.start_booking >= chosen_date,
                    Booking.start_booking < tomorrow,
                )
                .group_by(Booking.booking_number)
                .order_by(Booking.start_booking.asc())
                .all()
            )

    total_people = 0
    for booking in booking_list:
        total_people += booking[2]

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
    allow_operation = (
        db.session.query(Booking)
        .join(Table)
        .join(Restaurant)
        .join(Operator)
        .filter(
            Booking.booking_number == booking_number, Operator.id == current_user.id
        )
        .first()
    )
    if allow_operation is None:  # check if operator can see the page
        flash("Operation denied ")
        return redirect(
            url_for(".operator_reservations_list", restaurant_id=restaurant_id)
        )

    if request.method == "POST":
        for user_id in request.form.getlist("people"):
            aux = (
                db.session.query(Booking).filter(
                    Booking.user_id == user_id, Booking.booking_number == booking_number
                ).first()
            )
            aux.checkin = True
            db.session.commit()

    confirmed_booking = (
        db.session.query(Booking.confirmed_booking)
        .filter_by(booking_number=booking_number)
        .first()[0]
    )
    checkin_done = (
        db.session.query(Booking.checkin)
        .filter_by(booking_number=booking_number)
        .order_by(Booking.checkin.desc())
        .first()[0]
    )

    user_list = (
        db.session.query(User)
        .join(Booking)
        .filter(Booking.booking_number == booking_number)
        .all()
    )

    user_list_with_marks = []
    someone_marked = False

    for user in user_list:
        if user.is_marked():
            someone_marked = True
        user_list_with_marks.append((user, user.is_marked()))

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

    allow_operation = (
        db.session.query(Booking)
        .join(Table)
        .join(Restaurant)
        .join(Operator)
        .filter(
            Booking.booking_number == booking_number, Operator.id == current_user.id
        )
        .first()
    )
    if allow_operation is None:  # check if booking exisist
        flash("Operation denied")
        return redirect(
            url_for(".operator_reservations_list", restaurant_id=restaurant_id)
        )

    db.session.query(Booking).filter_by(booking_number=booking_number).delete()
    db.session.commit()

    flash("Reservation deleted", category="success")
    return redirect(url_for(".operator_reservations_list", restaurant_id=restaurant_id))


@restaurants.route("/bookings", methods=["GET", "POST"])
@login_required
@user_required
def user_booking_list():
    list_booking = db.session.query(Booking).filter(    Booking.user_id == current_user.id, Booking.start_booking >= date.today()).all()
    
    list_booking_with_restaurant=[]
    for booking in list_booking:
        restaurant = db.session.query(Restaurant).join(Table).filter(Table.id==booking.table_id).first()
        list_booking_with_restaurant.append((booking,restaurant))
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
    booking = db.session.query(Booking).filter_by(booking_number=booking_number, user_id=current_user.id).first()
    if booking is None:
        flash("Operation denied")
        return redirect(url_for('.user_booking_list'))

    db.session.query(Booking).filter_by(booking_number=booking_number).delete()
    db.session.commit()

    flash('Booking deleted', category='success')
    return redirect(url_for('.user_booking_list'))
