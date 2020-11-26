from urllib.parse import urlparse
from datetime import date
from flask import session

from .fixtures import app, client
from . import helpers
from monolith.api.users import delete_user, get_user_by_id
from monolith.api.operators import delete_operator


def test_unsubscribe_view_is_available(client):

    res = client.get("/unsubscribe")

    assert res.status_code == 302


def test_user_has_been_deleted_should_be_true(client):
    helpers.create_user(client)

    assert delete_user(1)


def test_operator_has_been_deleted_should_be_true(client):

    helpers.create_operator(client)

    assert delete_operator(1)


def test_marked_user_cannot_be_deleted_should_be_true(client):
    # BUG
    helpers.create_health_authority(client)
    helpers.create_user(client)
    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["fiscalcode"], "duration": 18},
        follow_redirects=True,
    )

    assert res.status_code == 200
    helpers.login_user(client)
    helpers.unsubscribe(client)
    user = get_user_by_id(1)
    #user = db.session.query(User).filter(User.email == "mariobrown@gmail.com").first()
    print(user)
    assert user["firstname"] == "mario"
