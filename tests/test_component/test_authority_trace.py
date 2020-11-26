from ..fixtures import app, client
from .. import helpers
from ..data import booking_people, user2, user3, table2


def test_ha_should_access_own_trace_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get(
        "trace",
        follow_redirects=False,
    )

    assert res.status_code == 200


def test_ha_should_trace_through_user_customer_same_time(client):
    # Create restaurant
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_restaurant(client)
    helpers.create_table(client)
    helpers.create_table(client, data=table2)
    helpers.logout(client)

    # Booking from a single user
    helpers.create_user(client)
    helpers.login_user(client)
    helpers.booking(client)
    helpers.logout(client)

    # Booking from a group of user
    helpers.create_user(client, data=user3)
    helpers.login_user(client, data=user3)
    helpers.booking_multiple_user(client)
    helpers.booking_confirm(client)  #!
    helpers.logout(client)

    b1 = db.session.query(Booking).all()[1]
    print(b1.checkin)
    print("USER: ", b1.user_id)
    print("BN: ", b1.booking_number)

    # Check-in
    helpers.login_operator(client)
    helpers.checkin_booking(client)
    helpers.checkin_booking_multiple_user2(client, 2)
    helpers.logout(client)

    helpers.create_health_authority(client)
    helpers.login_authority(client)

    client.post(
        "/marks/new",
        data={"identifier": user2["fiscalcode"], "duration": 15},
        follow_redirects=False,
    )

    res = client.post(
        "trace",
        data={"identifier": user2["fiscalcode"], "duration": 14},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"Traced contacts" in res.data
    # for value in booking_people.values():
    #     assert bytes(value, "utf-8") in res.data


def test_operator_should_not_access_trace_page(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get(
        "trace",
        follow_redirects=False,
    )

    assert res.status_code == 401


def test_user_should_not_access_trace_page(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get(
        "trace",
        follow_redirects=False,
    )

    assert res.status_code == 401


def test_anonymous_should_not_access_trace_page(client):
    res = client.get(
        "trace",
        follow_redirects=False,
    )

    assert res.status_code == 302
