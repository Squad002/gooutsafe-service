from monolith.models import Restaurant, RestaurantsPrecautions
from monolith.models.table import Table
from monolith import db


def add_new_restaurant(restaurant, prec_measures=None):
    q_rest = Restaurant.query.filter_by(
        lat=float(restaurant.lat),
        lon=float(restaurant.lon),
        operator_id=restaurant.operator_id,
    )
    if q_rest.first() is None:
        db.session.add(restaurant)
        db.session.commit()

        if prec_measures:
            for prec in prec_measures:
                new_restprec = RestaurantsPrecautions(
                    restaurant_id=restaurant.id, precautions_id=int(prec)
                )
                db.session.add(new_restprec)
                db.session.commit()

        return True
    else:
        return False


def check_restaurant_ownership(operator_id, restaurant_id):
    q = Restaurant.query.filter_by(id=restaurant_id, operator_id=operator_id)
    if q.first() is not None:
        return True
    else:
        return False


def add_new_table(table):
    q = Table.query.filter_by(name=table.name)
    if q.first() is None:
        db.session.add(table)
        db.session.commit()

        return True
    else:
        return False


def delete_table(table):
    q = Table.query.filter_by(id=table.id).first()
    if q is not None:
        db.session.delete(q)
        db.session.commit()

        return True
    else:
        return False


def check_table_existence(table):
    q = Table.query.filter_by(id=table.id).first()
    if q is not None:
        return True
    else:
        return False


def edit_table(table):
    table_to_edit = Table.query.filter_by(id=table.id).first()
    existing_table = Table.query.filter(
        Table.name == table.name,
        Table.id != table.id,
        Table.restaurant_id == table.restaurant_id,
    ).first()

    if existing_table is None:
        table_to_edit.name = table.name
        table_to_edit.seats = table.seats
        db.session.commit()
        return True
    else:
        return False
