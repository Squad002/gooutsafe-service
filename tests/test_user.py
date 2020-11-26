from monolith.api.users import get_user_by_id
from urllib.parse import urlparse
from datetime import datetime

from .fixtures import app, client
from . import helpers


def test_create_user_view_is_available(client):
    res = client.get("/register/user")

    assert res.status_code == 200


def test_create_user_view(client):
    helpers.create_user(client)

    res = get_user_by_id(1)

    assert res["email"] == "mariobrown@gmail.com"
    assert res["firstname"] == "mario"
    assert res["lastname"] == "brown"
    # TODO test birthdate
