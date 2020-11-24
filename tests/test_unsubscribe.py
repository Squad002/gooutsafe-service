from urllib.parse import urlparse
from datetime import date
from flask import session

from .fixtures import app, client, db
from . import helpers
from monolith.models import User
from monolith.api.users import delete_user
from monolith.api.operators import delete_operator


def test_unsubscribe_view_is_available(client):

    res = client.get("/unsubscribe")

    assert res.status_code == 302


def test_user_has_been_deleted_should_be_true(client, db):
    helpers.create_user(client)

    assert delete_user(1)



def test_operator_has_been_deleted_should_be_true(client, db):

    helpers.create_operator(client)

    assert delete_operator(1)


def test_marked_user_cannot_be_deleted_should_be_true(client, db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, duration=18)
    db.session.commit()

    helpers.login_user(client)
    helpers.unsubscribe(client)

    user = db.session.query(User).filter(User.email == "mariobrown@gmail.com").first()

    assert user.firstname == "mario"
