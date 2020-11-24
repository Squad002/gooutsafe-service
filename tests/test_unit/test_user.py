from tests.helpers import create_user
from monolith.models.review import Review
from ..fixtures import db, app, client
from .. import helpers

from datetime import datetime, timedelta


# Mark Tests
def test_has_been_marked_should_be_true(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user)
    db.session.commit()

    assert user.has_been_marked()


def test_is_marked_should_be_true(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user)
    db.session.commit()

    assert user.is_marked()


def test_is_marked_should_be_false(db):
    helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    db.session.commit()

    assert not user.is_marked()


def test_has_been_marked_should_be_false(db):
    helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    db.session.commit()

    assert not user.has_been_marked()


def test_get_mark_expiration_date_should_be_8_days_from_now(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, duration=7)
    db.session.commit()

    unmark_date = user.get_mark_expiration_date()

    assert unmark_date.date() == (datetime.utcnow() + timedelta(days=8)).date()


def test_get_remaining_mark_days(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, starting_date=datetime(2020, 10, 1), duration=14)
    db.session.commit()

    remaining_days = user.get_remaining_mark_days(from_date=datetime(2020, 10, 10))

    print(user.get_mark_expiration_date())

    assert remaining_days == 5


def test_get_last_mark_duration_should_be_ten(db):
    user = helpers.insert_user(db)

    ha1 = helpers.insert_health_authority(db)
    ha1.mark(user, starting_date=datetime(2020, 10, 1), duration=14)

    ha2 = helpers.insert_health_authority(db, data=helpers.health_authority2)
    ha2.mark(user, starting_date=datetime(2020, 10, 2), duration=10)

    assert user.get_last_mark_duration() == 10


# Review
def test_review_should_create_review_assosiaction(client, db):
    helpers.create_operator(client)
    restaurant = helpers.insert_restaurant_db(db)
    user = helpers.insert_user(db)

    user.review(restaurant, 5, "This was an amazing place to have a dinner!")
    db.session.commit()

    review = db.session.query(Review).filter(Review.user_id == user.id).first()

    assert review.user_id == user.id
    assert review.rating == 5
    assert review.message == "This was an amazing place to have a dinner!"
    assert review.created.date() == datetime.utcnow().date()


def test_user_auth_cycle(client):

    res = helpers.create_user(client)
    assert res.status_code == 302

    res = helpers.login_user(client)
    assert res.status_code == 302

    res = helpers.logout(client)
    assert res.status_code == 302

    helpers.login_user(client)
    res = helpers.unsubscribe(client)

    assert res.status_code == 302
