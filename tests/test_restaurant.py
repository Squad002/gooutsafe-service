from .fixtures import app, client, db
from . import helpers
from monolith.models import (
    Restaurant,
    Table,
    RestaurantsPrecautions,
    Precautions,
    Booking,
)
from monolith.models.menu import Menu, Food, MenuItems

from urllib.parse import urlparse

import io


def test_create_restaurant_view_is_available_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/restaurants/new")
    assert res.status_code == 200


def test_create_restaurant_view_is_notavailable_anonymous(client):
    res = client.get("/restaurants/new")
    assert res.status_code == 401


def test_create_restaurant_view_is_notavailable_user(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/new")
    assert res.status_code == 401


def test_create_restaurant_view_is_notavailable_ha(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/new")
    assert res.status_code == 401


def test_restaurant_sheet(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.restaurant_sheet(client)
    restaurant = db.session.query(Restaurant).filter_by(id=1).first()

    restaurant_precautions = (
        db.session.query(Precautions.name)
        .filter(
            Precautions.id == RestaurantsPrecautions.precautions_id,
            RestaurantsPrecautions.restaurant_id == 1,
        )
        .all()
    )

    assert res.status_code == 200

    for prec in restaurant_precautions:
        assert bytes(prec.name, "utf-8") in res.data

    assert bytes(restaurant.name, "utf-8") in res.data
    assert bytes(restaurant.cuisine_type.value, "utf-8") in res.data
    assert bytes(str(restaurant.opening_hours), "utf-8") in res.data
    assert bytes(str(restaurant.closing_hours), "utf-8") in res.data
    assert bytes(str(restaurant.phonenumber), "utf-8") in res.data
    for menu in restaurant.menus:
        assert bytes(menu.name, "utf-8") in res.data


def test_restaurant_sheet_not_existing_restaurant(client):
    res = helpers.restaurant_sheet(client)

    assert res.status_code == 404


def test_create_restaurant(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    res = helpers.create_restaurant(client)


    fetched_restaurant = (
        db.session.query(Restaurant).filter_by(id=1, operator_id=1).first()
    )

    assert res.status_code == 302
    assert fetched_restaurant.name == "Trattoria da Fabio"
    assert fetched_restaurant.phonenumber == "555123456"
    assert fetched_restaurant.lat == 40.720586
    assert fetched_restaurant.lon == 10.10
    assert fetched_restaurant.time_of_stay == 30
    assert fetched_restaurant.opening_hours == 12
    assert fetched_restaurant.closing_hours == 24
    assert fetched_restaurant.cuisine_type.name == "ETHNIC"
    assert fetched_restaurant.operator.id == 1
    assert urlparse(res.location).path == "/restaurants/mine"


def test_upload_view_available(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = client.get("/restaurants/1/upload")
    assert res.status_code == 200


def test_upload(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    file_path = "./monolith/static/uploads/1/pizza.jpeg"
    data = {"file": open(file_path, "rb")}
    res = client.post("/restaurants/1/upload", data=data)
    assert res.status_code == 302


def test_upload_restaurant_not_exists(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/restaurants/1/upload")
    assert res.status_code == 404


def test_bad_upload(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    file_name = "uploads/1/yolo.txt"
    data = {"file": (io.BytesIO(b"bad stuff"), file_name)}
    res = client.post("/restaurants/1/upload", data=data)
    assert res.status_code == 400


def test_create_restaurant_bad_data(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)

    data = dict(
        name="Trattoria da Pippo",
        phonenumber=651981916,
        lat=-500.75,
        lon=900.98,
        time_of_stay=200,
        cuisine_type="ETHNIC",
        opening_hours=12,
        closing_hours=24,
        operator_id=1,
    )

    res = helpers.create_restaurant(client, data)
    fetched_restaurant = db.session.query(Restaurant).filter_by(operator_id=1).first()

    assert fetched_restaurant is None
    assert res.status_code == 400


def test_create_duplicate_restaurant(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    restaurant = dict(
        name="Trattoria da Pippo",
        phonenumber=615543,
        lat=40.720586,
        lon=10.10,
        time_of_stay=30,
        cuisine_type="ETHNIC",
        opening_hours=12,
        closing_hours=24,
        operator_id=1,
    )

    res = helpers.create_restaurant(client, restaurant)
    fetched_dup_restaurant = db.session.query(Restaurant).filter_by(id=2).first()

    assert res.status_code == 400
    assert fetched_dup_restaurant is None


def test_create_table_view_is_available_operator(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = client.get("/restaurants/1/tables/new")
    assert res.status_code == 200


def test_create_table_view_is_notavailable_anonymous(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    res = client.get("/restaurants/1/tables/new")
    assert res.status_code == 401


def test_create_table_view_is_notavailable_user(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/1/tables/new")
    assert res.status_code == 401


def test_create_table_view_is_notavailable_ha(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.login_operator(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/tables/new")
    assert res.status_code == 401


def test_create_table(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.create_table(client)
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 302
    assert fetched_table.name == "A10"
    assert fetched_table.seats == 10
    assert urlparse(res.location).path == "/restaurants/1/tables"


def test_create_table_restaurant_not_exists(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = helpers.create_table(client)
    assert res.status_code == 404


def test_create_table_bad_data(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    data = dict(name="A10", seats=-5, restaurant_id=1)
    res = helpers.create_table(client, data=data)

    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 400
    assert fetched_table is None


def test_create_duplicate_table(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    helpers.create_table(client)
    data = dict(name="A10", seats=2, restaurant_id=1)
    res = helpers.create_table(client, data=data)

    fetched_table = db.session.query(Table).filter_by(id=2).first()

    assert res.status_code == 400
    assert fetched_table is None


def test_create_table_not_owned_restaurant(client, db):
    helpers.create_operator(client)

    helpers.create_operator(client, helpers.operator3)

    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.login_operator(client, helpers.operator3)
    res = helpers.create_table(client)
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 401
    assert fetched_table is None


def test_delete_table_view_is_notavailable_user(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/1/tables/delete/1")
    assert res.status_code == 401


def test_delete_table_view_is_notavailable_anonymous(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    res = client.get("/restaurants/1/tables/delete/1")
    assert res.status_code == 401


def test_delete_table_view_is_available_operator(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = client.get("/restaurants/1/tables/delete/1")
    assert res.status_code == 200


def test_delete_table_view_is_notavailable_ha(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/tables/delete/1")
    assert res.status_code == 401


def test_delete_table(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    helpers.create_table(client)
    res = helpers.delete_table(client)

    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 200
    assert fetched_table is None


def test_delete_table_not_exists(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.delete_table(client)

    assert res.status_code == 404


def test_delete_table_not_owned_restaurant(client, db):
    helpers.create_operator(client)

    helpers.create_operator(client, helpers.operator3)

    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.login_operator(client, helpers.operator3)
    res = helpers.delete_table(client)
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 401
    assert fetched_table is not None


def test_delete_table_bad_table_id(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = helpers.delete_table(client, table_id=9)

    assert res.status_code == 404


def test_delete_table_bad_restaurant_id(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = helpers.delete_table(client, restaurant_id=5, table_id=1)

    assert res.status_code == 401


def test_edit_table_view_is_notavailable_user(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/1/tables/edit/1")
    assert res.status_code == 401


def test_edit_table_view_is_notavailable_anonymous(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    res = client.get("/restaurants/1/tables/edit/1")
    assert res.status_code == 401


def test_edit_table_view_is_available_operator(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = client.get("/restaurants/1/tables/edit/1")
    assert res.status_code == 200


def test_edit_table_view_is_notavailable_ha(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.login_operator(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/tables/edit/1")
    assert res.status_code == 401


def test_edit_table(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    data = dict(id=1, name="A5", seats=6)
    res = helpers.edit_table(client, data=data)

    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 302
    assert fetched_table.name == "A5"
    assert fetched_table.seats == 6
    assert urlparse(res.location).path == "/restaurants/1/tables"


def test_edit_table_to_one_with_same_name(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    helpers.create_table(client)

    data = dict(name="A5", seats=6)
    helpers.create_table(client, data=data)

    data["name"] = "A10"
    data["seats"] = 1
    res = helpers.edit_table(client, table_id=2, data=data)

    fetched_table = db.session.query(Table).filter_by(id=2).first()

    assert res.status_code == 400
    assert fetched_table.name == "A5"
    assert fetched_table.seats == 6


def test_edit_table_not_exists(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.edit_table(client)

    assert res.status_code == 404


def test_edit_table_not_owned_restaurant(client, db):
    helpers.create_operator(client)

    helpers.create_operator(client, helpers.operator3)

    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.login_operator(client, helpers.operator3)

    table_data = dict(id=1, name="A1", seats=1)
    res = helpers.edit_table(client, table_data)
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res.status_code == 401
    assert fetched_table.name != "A1"
    assert fetched_table.seats != 1


def test_edit_table_bad_restaurant_id(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = helpers.edit_table(client, restaurant_id=2)

    assert res.status_code == 401


def test_edit_table_bad_table_id(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = helpers.edit_table(client, table_id=2)

    assert res.status_code == 404


def test_edit_table_bad_data(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    bad_table = dict(name="A10", seats=-10)

    res = helpers.edit_table(client, data=bad_table)

    assert res.status_code == 400


def test_operator_view_isavailable_operator(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/restaurants/mine")
    assert res.status_code == 200


def test_operator_view_isnotavailable_anonymous(client, db):
    res = client.get("/restaurants/mine")
    assert res.status_code == 401


def test_operator_view_isnotavailable_user(client, db):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/mine")
    assert res.status_code == 401


def test_operator_view_isnotavailable_ha(client, db):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/mine")
    assert res.status_code == 401


def test_operator_restaurant(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.operator_restaurants(client)
    op_restaurants = db.session.query(Restaurant).filter_by(operator_id=1)

    assert res.status_code == 200
    for rest in op_restaurants:
        assert bytes(rest.name, "utf-8") in res.data


def test_operator_restaurant_empty(client, db):
    helpers.create_operator(client)

    helpers.create_operator(client, helpers.operator3)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.login_operator(client, helpers.operator3)
    res = helpers.operator_restaurants(client)
    op_restaurants = db.session.query(Restaurant).filter_by(operator_id=1)

    assert res.status_code == 200
    for rest in op_restaurants:
        assert bytes(rest.name, "utf-8") not in res.data


def test_restaurants_available_anonymous(client):
    res = client.get("/restaurants")
    assert res.status_code == 200


def test_restaurants_available_user(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants")
    assert res.status_code == 200


def test_restaurants_available_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/restaurants")
    assert res.status_code == 200


def test_restaurants_available_ha(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants")
    assert res.status_code == 200


def test_restaurants_logged(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = client.get("/restaurants")
    q_rest = db.session.query(Restaurant)

    assert res.status_code == 200
    for rest in q_rest:
        assert bytes(rest.name, "utf-8") in res.data


def test_restaurants_notlogged(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    res = client.get("/restaurants")
    q_rest = db.session.query(Restaurant)

    assert res.status_code == 200
    for rest in q_rest:
        assert bytes(rest.name, "utf-8") in res.data


def test_tables_notavailable_user(client):
    helpers.create_operator(client)
    helpers.create_user(client)

    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.login_user(client)

    res = client.get("/restaurants/1/tables")
    assert res.status_code == 401


def test_tables_notavailable_anonymous(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    res = client.get("/restaurants/1/tables")
    assert res.status_code == 401


def test_tables_available_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = client.get("/restaurants/1/tables")
    assert res.status_code == 200


def test_tables_notavailable_ha(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/tables")
    assert res.status_code == 401


def test_tables(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = client.get("/restaurants/1/tables")
    q_table = db.session.query(Table).filter_by(restaurant_id=1)

    assert res.status_code == 200
    for table in q_table:
        assert bytes(table.name, "utf-8") in res.data


def test_tables_not_exists(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/restaurants/1/tables")
    assert res.status_code == 404


def test_tables_not_owned_restaurant(client, db):
    helpers.create_operator(client)

    helpers.create_operator(client, helpers.operator3)

    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.login_operator(client, helpers.operator3)

    res = client.get("/restaurants/1/tables")

    assert res.status_code == 401


def test_create_menu_isnotavailable_anonymous(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    res = client.get("/restaurants/1/menus/new")

    assert res.status_code == 401


def test_create_menu_isnotavailable_user(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/1/menus/new")

    assert res.status_code == 401


def test_create_menu_isavailable_operator(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = client.get("/restaurants/1/menus/new")

    assert res.status_code == 200


def test_create_menu_isnotavailable_ha(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/menus/new")

    assert res.status_code == 401


def test_create_menu(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    #helpers.create_restaurant(client)

    res = helpers.create_menu(client)

    assert res.status_code == 302


def test_create_duplicate_menu(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    helpers.create_menu(client)
    res = helpers.create_menu(client)

    assert res.status_code == 400


def test_create_menu_duplicate_foods(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    res = helpers.create_menu(client, helpers.menu_dup_food)

    assert res.status_code == 400


def test_create_menu_not_owned_restaurant(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.logout(client)

    helpers.create_operator(client, helpers.operator3)
    helpers.login_operator(client, helpers.operator3)
    helpers.create_menu(client)
    res = helpers.create_menu(client)

    assert res.status_code == 401


def test_create_menu_bad_data(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    bad_menu = helpers.menu
    bad_menu["menu_name"] = ""
    res = helpers.create_menu(client, data=bad_menu)
    assert res.status_code == 400

    bad_menu["menu_name"] = "Trial menu1"
    bad_menu["name"] = ""
    res = helpers.create_menu(client, data=bad_menu)
    assert res.status_code == 400

    bad_menu["menu_name"] = "Trial menu2"
    bad_menu["name"] = "Trial food"
    bad_menu["price"] = ""
    res = helpers.create_menu(client, data=bad_menu)
    assert res.status_code == 400

    bad_menu["menu_name"] = "Trial menu3"
    bad_menu["price"] = "-5"
    res = helpers.create_menu(client, data=bad_menu)
    assert res.status_code == 400

    bad_menu["menu_name"] = "Trial menu4"
    bad_menu["price"] = "5"
    bad_menu["category"] = "WRONG_CAT"
    res = helpers.create_menu(client, data=bad_menu)
    assert res.status_code == 400
    bad_menu["category"] = "DRINKS"


def test_show_menu(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)

    helpers.create_menu(client)

    res = helpers.show_menu(client)
    menu = db.session.query(Menu).filter(Menu.restaurant_id == 1, Menu.id == 1).first()

    assert res.status_code == 200
    assert bytes(menu.name, "utf-8") in res.data
    for food in menu.foods:
        assert bytes(food.name, "utf-8") in res.data
        assert bytes(str(food.price), "utf-8") in res.data
        assert bytes(food.category.value, "utf-8") in res.data


def test_show_menu_not_exists(client):
    res = helpers.show_menu(client)

    assert res.status_code == 404


def test_restaurants(client, db):
    helpers.insert_restaurant_db(db)
    allrestaurants = db.session.query(Restaurant).all()
    assert len(allrestaurants) == 1


def test_restaurant_booking_is_avaible_logged_user(
    client,
):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/restaurants/1/booking")
    assert res.status_code == 200


def test_restaurant_booking_not_avaible_ha(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/restaurants/1/booking")
    assert res.status_code == 401


def test_restaurant_booking_not_avaible_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)

    res = client.get("/restaurants/1/booking")
    assert res.status_code == 401


def test_restaurant_booking_not_avaible_anonymous(client):
    res = client.get("/restaurants/1/booking")
    assert res.status_code == 401


def test_restaurant_booking(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = helpers.booking(client)

    assert res.status_code == 302


def test_restaurant_all_tables_booked(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client)

    res = helpers.booking(client)

    assert res.status_code == 200


def test_multiple_booking(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client)

    assert res.status_code == 302


def test_multiple_booking_double_user(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client, double_fiscal_code_user=True)

    assert res.status_code == 200


def test_multiple_booking_double_email(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)

    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client, double_email_user=True)

    assert res.status_code == 200


def test_list_reservation(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client)
    helpers.logout(client)

    helpers.login_operator(client)
    res = helpers.reservation_list(client)

    assert res.status_code == 200


def test_reservation(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    res = helpers.booking_multiple_user(client)
    res = helpers.booking_confirm(client)
    helpers.logout(client)

    helpers.login_operator(client)
    res = helpers.reservation(client)

    assert res.status_code == 200


def test_user_bookings(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)

    res = helpers.bookings(client)

    assert res.status_code == 200
    assert b"Trattoria da Fabio" in res.data
    assert b"8:00" in res.data


def test_user_delete_booking(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)

    res = helpers.delete_booking_by_user(client)

    assert res.status_code == 302
    assert db.session.query(Booking).filter_by(booking_number=1).first() is None


def test_user_delete_double_booking(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)

    res = helpers.delete_booking_by_user(client)
    res = helpers.delete_booking_by_user(client)

    assert res.status_code == 302
    assert db.session.query(Booking).filter_by(booking_number=1).first() is None


def test_operator_delete_booking(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)

    helpers.logout(client)

    helpers.login_operator(client)
    res = helpers.delete_booking_by_operator(client)

    assert res.status_code == 302
    assert db.session.query(Booking).filter_by(booking_number=1).first() is None


def test_checkin(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)
    helpers.logout(client)

    helpers.login_operator(client)
    res = helpers.checkin_booking(client)

    assert b"Check-in done" in res.data
    assert res.status_code == 200


def test_checkin_multiple_people(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.logout(client)

    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking_multiple_user(client)
    helpers.booking_confirm(client)
    helpers.logout(client)

    helpers.login_operator(client)
    res = helpers.checkin_booking_multiple_user(client)

    assert b"Check-in done" in res.data
    assert res.status_code == 200
