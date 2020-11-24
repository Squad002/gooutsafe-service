from datetime import date
from monolith.models.menu import Menu, Food
from monolith.models import (
    User,
    Restaurant,
    RestaurantsPrecautions,
    HealthAuthority,
    Precautions,
)
from tests.data import (
    precautions,
    booking,
    booking_people,
    booking_people_double_fiscal_code,
    booking_people_double_email,
    booking1,
    booking2,
    checkin_people,
    checkin_multiple_people,
    checkin_multiple_people2,
)
from werkzeug.datastructures import MultiDict


# DATA
# ! IMPORTANT
# FROM NOW ON LET'S PUT THE DEFINITION OF THE DATA IN tests/data.py, NOT HERE. IN ORDER TO HAVE A SINGLE TRUTH
# HERE ONLY THE METHODS

user = dict(
    email="mariobrown@gmail.com",
    firstname="mario",
    lastname="brown",
    password="1234",
    dateofbirth=date(1995, 12, 31),
    fiscalcode="RSSMRA95T31H501R",
    phonenumber="+39331303313094",
)

user2 = dict(
    email="mariobrown@gmail.com",
    firstname="mario",
    lastname="brown",
    password="1234",
    dateofbirth="1995-12-31",
    fiscalcode="RSSMRA95T31H501R",
    phonenumber="+39331303313094",
)

operator = dict(
    email="giuseppebrown@lalocanda.com",
    firstname="giuseppe",
    lastname="yellow",
    password="5678",
    dateofbirth="01/01/1963",
    fiscalcode="YLLGPP63A01B519O",
    phonenumber="+39331303313094",
)

operator2 = dict(
    email="giuseppebrown@lalocanda.com",
    firstname="giuseppe",
    lastname="yellow",
    password="5678",
    dateofbirth="1963-01-01",
    fiscalcode="YLLGPP63A01B519O",
    phonenumber="+39331303313094",
)


operator3 = dict(
    email="pippopioppo@ploppi.com",
    firstname="pippo",
    lastname="pioppo",
    password="ploppi",
    dateofbirth="1963-01-01",
    fiscalcode="YLLGPP63A01B519O",
    phonenumber="+39331303313094",
)

health_authority = dict(
    email="canicatti@asl.it",
    name="ASL Canicattì",
    password="cani123",
    phonenumber="0808403849",
    country="Italy",
    state="AG",
    city="Canicattì",
    lat=37.36,
    lon=13.84,
)

health_authority2 = dict(
    email="roma@asl.it",
    name="ASL Roma",
    password="romasqpr",
    phonenumber=" 0639741322",
    country="Italy",
    state="RM",
    city="Roma",
    lat=41.89,
    lon=12.49,
)

restaurant = dict(
    name="Trattoria da Fabio",
    phonenumber=555123456,
    lat=40.720586,
    lon=10.10,
    time_of_stay=30,
    cuisine_type="ETHNIC",
    opening_hours=12,
    closing_hours=24,
    operator_id=1,
)


menu = MultiDict(
    [
        ("menu_name", "Trial menu"),
        ("name", "Pepperoni pizza"),
        ("price", 5.0),
        ("category", "PIZZAS"),
    ]
)


menu_dup_food = MultiDict(
    [
        ("menu_name", "Trial menu"),
        ("name", "Pepperoni pizza"),
        ("price", 5.0),
        ("category", "PIZZAS"),
        ("name", "Pepperoni pizza"),
        ("price", 10),
        ("category", "DRINKS"),
    ]
)


table = dict(name="A10", seats=10, restaurant_id=1)

# CREATION


def create_user(client, data=user2):
    return client.post(
        "/register/user",
        data=data,
        follow_redirects=False,
    )


# ! It's here just as a reference. The testing procedure should not need to work directly
# !     with the database when a view to insert the user is available.
# TODO in the future if not needed, and the test goes as planned, it can be deleted.
def insert_user(db, data=user) -> User:
    temp = User(**data)
    db.session.add(temp)
    db.session.commit()
    return temp


def insert_restaurant_db(db, data=restaurant) -> Restaurant:
    temp = Restaurant(**data)
    db.session.add(temp)
    db.session.commit()
    return temp


def insert_precautions(db, precautions=precautions):
    for p in precautions:
        db.session.add(Precautions(**p))
    db.session.commit()


def insert_precautions_in_restaurant(
    db, restaurant: Restaurant, precautions_id=[1, 2, 4]
):
    for precaution_id in precautions_id:
        db.session.add(
            RestaurantsPrecautions(
                restaurant_id=restaurant.id, precautions_id=precaution_id
            )
        )
    db.session.commit()


def insert_complete_restaurant(db):
    restaurant = insert_restaurant_db(db)
    insert_precautions(db)
    insert_precautions_in_restaurant(db, restaurant=restaurant)
    return restaurant


def create_operator(client, data=operator2):
    return client.post(
        "/register/operator",
        data=data,
        follow_redirects=False,
    )


def create_operator2(client, data=operator):
    return client.post(
        "/register/operator",
        data=data,
        follow_redirects=False,
    )


def create_health_authority(client, data=health_authority):
    return client.post(
        "/register/authority",
        data=data,
        follow_redirects=False,
    )


def create_restaurant(client, data=restaurant):
    return client.post(
        "/restaurants/new",
        data=data,
        follow_redirects=False,
    )


def create_menu(client, data=menu):
    return client.post(
        "/restaurants/1/menus/new",
        data=data,
        follow_redirects=False,
    )


def show_menu(client, restaurant_id=1, menu_id=1):
    return client.get(
        "/restaurants/" + str(restaurant_id) + "/menus/show/" + str(menu_id),
        follow_redirects=False,
    )


def restaurant_sheet(client, restaurant_id=1):
    return client.get("/restaurants/" + str(restaurant_id), follow_redirects=False)


def operator_restaurants(client):
    return client.get("/restaurants/mine", follow_redirects=False)


def create_table(client, restaurant_id=1, data=table):
    return client.post(
        "/restaurants/" + str(restaurant_id) + "/tables/new",
        data=data,
        follow_redirects=False,
    )


def edit_table(client, restaurant_id=1, table_id=1, data=table):
    return client.post(
        "/restaurants/" + str(restaurant_id) + "/tables/edit/" + str(table_id),
        data=data,
        follow_redirects=False,
    )


def delete_table(client, restaurant_id=1, table_id=1, data=table):
    return client.post(
        "/restaurants/" + str(restaurant_id) + "/tables/delete/" + str(table_id),
        data=data,
        follow_redirects=False,
    )


def insert_health_authority(db, data=health_authority) -> HealthAuthority:
    temp = HealthAuthority(**data)
    db.session.add(temp)
    db.session.commit()
    return temp


# OTHER


def login_user(client, data=user):
    return client.post(
        "/login/user",
        data=data,
        follow_redirects=False,
    )


def login_operator(client, data=operator):
    return client.post(
        "/login/operator",
        data=data,
        follow_redirects=False,
    )


def logout(client):
    return client.get(
        "/logout",
        follow_redirects=False,
    )


def login_authority(client, data=health_authority):
    return client.post(
        "/login/authority",
        data=data,
        follow_redirects=False,
    )


def booking(client, data=booking1):
    return client.post(
        "/restaurants/1/booking",
        data=data,
        follow_redirects=False,
    )


def delete_booking_by_user(client, book_number=1):
    return client.get("/bookings/delete/" + str(book_number), follow_redirects=False)


def delete_booking_by_operator(client, restaurant_id=1, book_number=1):
    return client.get(
        "/restaurants/"
        + str(restaurant_id)
        + "/reservations/delete/"
        + str(book_number),
        follow_redirects=False,
    )


def booking_multiple_user(client, data=booking2):
    return client.post(
        "/restaurants/1/booking",
        data=data,
        follow_redirects=False,
    )


def booking_confirm(
    client, double_fiscal_code_user=False, double_email_user=False, data=booking_people
):
    if double_fiscal_code_user:
        data = booking_people_double_fiscal_code
    elif double_email_user:
        data = booking_people_double_email

    return client.post(
        "/restaurants/1/booking/confirm",
        data=data,
        follow_redirects=False,
    )


def checkin_booking_multiple_user(client, reservation_id=1):
    return client.post(
        f"/restaurants/1/reservations/{reservation_id}",
        data=checkin_multiple_people,
        follow_redirects=True,
    )


def checkin_booking_multiple_user2(client, reservation_id=1):
    return client.post(
        f"/restaurants/1/reservations/{reservation_id}",
        data=checkin_multiple_people2,
        follow_redirects=True,
    )


def bookings(client):
    return client.get(
        "/bookings",
        follow_redirects=False,
    )


def checkin_booking(client):
    return client.post(
        "/restaurants/1/reservations/1",
        data=checkin_people,
        follow_redirects=False,
    )


def unsubscribe(client):
    return client.get(
        "/unsubscribe",
        follow_redirects=False,
    )


def reservation_list(client):
    return client.post(
        "/restaurants/1/reservations",
        data={"date": date.today()},
        follow_redirects=False,
    )


def reservation(client):
    return client.get(
        "/restaurants/1/reservations/1",
        follow_redirects=False,
    )
