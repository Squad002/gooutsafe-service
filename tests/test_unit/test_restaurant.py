from ..fixtures import db, client, app
from .. import helpers
from monolith.models import (
    Restaurant,
    Precautions,
    RestaurantsPrecautions,
    Operator,
    Table,
)
from monolith.controllers import restaurant


def test_add_new_restaurant_no_prec(client, db):
    helpers.create_operator(client)
    new_restaurant = Restaurant(**helpers.restaurant)

    res = restaurant.add_new_restaurant(new_restaurant)
    q_restaurant = (
        db.session.query(Restaurant).filter_by(name=new_restaurant.name).first()
    )
    q_restprec = (
        db.session.query(RestaurantsPrecautions)
        .filter_by(restaurant_id=new_restaurant.id)
        .first()
    )

    assert res == True
    assert q_restaurant is not None
    assert q_restprec is None


def test_add_new_restaurant(client, db):
    helpers.create_operator(client)
    new_restaurant = Restaurant(**helpers.restaurant)

    helpers.insert_precautions(db)
    res = restaurant.add_new_restaurant(new_restaurant, [1, 2])
    q_rest = db.session.query(Restaurant).filter_by(name=new_restaurant.name).first()
    q_restprec = (
        db.session.query(RestaurantsPrecautions)
        .filter_by(restaurant_id=new_restaurant.id)
        .first()
    )

    assert res == True
    assert q_rest is not None
    assert q_restprec is not None


def test_already_added_restaurant(client, db):
    helpers.create_operator(client)
    op = db.session.query(Operator).filter_by(id=1).first()
    new_restaurant1 = Restaurant(**helpers.restaurant)

    new_restaurant2 = Restaurant(
        name="Trattoria da Luca",
        phonenumber=651981916,
        lat=40.720586,
        lon=10.10,
        time_of_stay=30,
        operator_id=op.id,
    )

    restaurant.add_new_restaurant(new_restaurant1)
    res = restaurant.add_new_restaurant(new_restaurant2)

    assert res == False
    assert (
        db.session.query(Restaurant).filter_by(name=new_restaurant2.name).first()
        is None
    )


def test_add_new_table(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table = Table(**helpers.table)
    res = restaurant.check_table_existence(new_table)
    assert res == False
    res = restaurant.add_new_table(new_table)
    assert res == True
    res = restaurant.check_table_existence(new_table)
    assert res == True
    assert db.session.query(Table).filter_by(name=new_table.name).first() is not None


def test_delete_table_successful(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table = Table(**helpers.table)
    restaurant.add_new_table(new_table)

    table_to_delete = Table(**helpers.table)
    table_to_delete.id = 1

    res = restaurant.delete_table(table_to_delete)

    assert res == True
    assert db.session.query(Table).filter_by(name=new_table.id).first() is None


def test_delete_table_unsuccessful(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table = Table(**helpers.table)
    restaurant.add_new_table(new_table)

    table_to_delete = Table(**helpers.table)
    table_to_delete.id = 2

    res = restaurant.delete_table(table_to_delete)

    assert res == False
    assert db.session.query(Table).filter_by(id=new_table.id).first() is not None


def test_already_added_table(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table1 = Table(**helpers.table)
    restaurant.add_new_table(new_table1)

    new_table2 = Table(name="A10", seats=5, restaurant_id=new_restaurant.id)
    res = restaurant.add_new_table(new_table2)

    assert res == False
    assert (
        db.session.query(Table)
        .filter_by(name=new_table2.name, seats=new_table2.seats)
        .first()
        is None
    )


def test_edit_table_successful(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table = Table(**helpers.table)
    restaurant.add_new_table(new_table)

    res = restaurant.edit_table(Table(id=1, name="A10", seats=3, restaurant_id=1))
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res == True
    assert fetched_table.name == "A10"
    assert fetched_table.seats == 3
    assert fetched_table.restaurant_id == 1


def test_edit_table_unsuccessful(client, db):
    helpers.create_operator(client)

    new_restaurant = Restaurant(**helpers.restaurant)
    restaurant.add_new_restaurant(new_restaurant)

    new_table = Table(**helpers.table)
    restaurant.add_new_table(new_table)
    restaurant.add_new_table(Table(name="A8", seats=5, restaurant_id=1))

    res = restaurant.edit_table(Table(id=1, name="A8", seats=1, restaurant_id=1))
    fetched_table = db.session.query(Table).filter_by(id=1).first()

    assert res == False
    assert fetched_table.name == "A10"
    assert fetched_table.seats == 10


def test_check_restaurant_ownership(client, db):
    helpers.create_operator(client)
    op1 = db.session.query(Operator).filter_by(id=1).first()
    helpers.create_operator2(client, helpers.operator3)
    op2 = db.session.query(Operator).filter_by(id=2).first()

    new_restaurant = Restaurant(**helpers.restaurant)
    new_restaurant.operator_id = op1.id
    restaurant.add_new_restaurant(new_restaurant)

    res = restaurant.check_restaurant_ownership(op1.id, new_restaurant.id)
    assert res == True

    res = restaurant.check_restaurant_ownership(op2.id, new_restaurant.id)
    assert res == False
