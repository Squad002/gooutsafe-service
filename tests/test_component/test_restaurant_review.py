from tests import data, helpers
from tests.fixtures import app, client, db
from urllib.parse import urlparse


# TODO merge with the restaurant page test


def test_user_should_see_review_form(client, db):
    helpers.create_user(client)
    helpers.login_user(client)
    helpers.insert_complete_restaurant(db)

    res = visit_restaurant_page(client)

    assert res.status_code == 200
    assert b"Add your review" in res.data
    assert b"Your rating" in res.data
    assert b"Your review" in res.data


def test_user_should_create_review(client, db):
    helpers.create_user(client)
    helpers.login_user(client)
    helpers.insert_complete_restaurant(db)

    res = create_review(client)

    assert res.status_code == 200
    assert b"mario" in res.data
    assert b"5" in res.data
    assert (
        b"It was a delicious dinner, but initially the service was not so excellent in the speed of serving the meals."
        in res.data
    )


# def test_user_should_create_review2(client, db):
#     helpers.insert_complete_restaurant(db)

#     helpers.create_user(client)
#     helpers.login_user(client)
#     res = create_review(client, rating=4)
#     helpers.logout(client)

#     helpers.create_user(client, data=data.user3)
#     helpers.login_user(client)
#     res = create_review(client, rating=2)
#     helpers.logout(client)

#     from monolith.services.background.tasks import compute_restaurants_rating_average

#     compute_restaurants_rating_average()

#     assert res.status_code == 200
#     assert b'<div class="content">3</div>' in res.data


def test_user_should_create_review_if_already_did(client, db):
    helpers.create_user(client)
    helpers.login_user(client)
    helpers.insert_complete_restaurant(db)

    create_review(client)
    res = create_review(client, rating=3)

    assert res.status_code == 200
    assert b"You already reviewed this restaraunt"


def test_user_should_not_create_review_when_message_is_less_than_30_character(
    client, db
):
    helpers.create_user(client)
    helpers.login_user(client)
    helpers.insert_complete_restaurant(db)

    res = client.post(
        "/restaurants/1",
        data=dict(rating=4, message="It was a"),
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"The review should be at least of 30 characters." in res.data


# def test_user_should_not_create_review_when_rating_bigger_than_5(client, db):
#     helpers.create_user(client)
#     helpers.login_user(client)
#     helpers.insert_complete_restaurant(db)

#     res = create_review(client, rating=6)

#     assert res.status_code == 200
#     assert b"The number of stars must be between 1 and 5" in res.data


# def test_user_should_not_create_review_when_rating_is_zero(client, db):
#     helpers.create_user(client)
#     helpers.login_user(client)
#     helpers.insert_complete_restaurant(db)

#     res = create_review(client, rating=0)

#     assert res.status_code == 200
#     assert b"This field is required" in res.data


# def test_user_should_not_create_review_when_rating_smaller_than_zero(client, db):
#     helpers.create_user(client)
#     helpers.login_user(client)
#     helpers.insert_complete_restaurant(db)

#     res = create_review(client, rating=-1)

#     assert res.status_code == 200
#     assert b"The number of stars must be between 1 and 5" in res.data


def test_authority_should_not_see_the_review_form(client, db):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.insert_complete_restaurant(db)

    res = visit_restaurant_page(client)

    assert res.status_code == 200
    assert b"Add your review" not in res.data
    assert b"Your rating" not in res.data
    assert b"Your review" not in res.data


# Here the HA cannot see the form, but if it knows the endpoint, then it still can make a request
def test_authority_should_not_create_review(client, db):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.insert_complete_restaurant(db)

    res = create_review(client)

    assert res.status_code == 200
    assert b"Only a logged user can review a restaurant." in res.data


def test_operator_should_not_see_the_review_form(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.insert_complete_restaurant(db)

    res = visit_restaurant_page(client)

    assert res.status_code == 200
    assert b"Add your review" not in res.data
    assert b"Your rating" not in res.data
    assert b"Your review" not in res.data


# Here the Operator cannot see the form, but if it knows the endpoint, then it still can make a request
def test_operator_should_not_create_review(client, db):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.insert_complete_restaurant(db)

    res = create_review(client)

    assert res.status_code == 200
    assert b"Only a logged user can review a restaurant." in res.data


def test_anonymous_user_should_see_review_form(client, db):
    helpers.insert_complete_restaurant(db)

    res = visit_restaurant_page(client)

    assert res.status_code == 200
    assert b"Add your review" in res.data
    assert b"Your rating" in res.data
    assert b"Your review" in res.data


def test_anonymous_user_should_be_redirected_on_login_page_when_create_review(
    client, db
):
    helpers.insert_complete_restaurant(db)

    res = create_review(client, redirect=False)

    assert res.status_code == 302
    assert urlparse(res.location).path == "/login/user"


# Helpers methods


def create_review(client, message=None, rating=5, redirect=True):
    if not message:
        message = "It was a delicious dinner, but initially the service was not so excellent in the speed of serving the meals."

    return client.post(
        "/restaurants/1",
        data=dict(
            rating=rating,
            message=message,
        ),
        follow_redirects=redirect,
    )


def visit_restaurant_page(client):
    return client.get(
        "/restaurants/1",
        follow_redirects=False,
    )
