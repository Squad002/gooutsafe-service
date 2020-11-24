from urllib.parse import urlparse
from datetime import datetime

from .fixtures import app, client, db
from . import helpers
from monolith.models import User


def test_create_user_view_is_available(client):
    res = client.get("/register/user")

    assert res.status_code == 200


def test_create_user_view(client, db):
    res = helpers.create_user(client)

    fetched_user = (
        db.session.query(User).filter(User.email == "mariobrown@gmail.com").first()
    )

    assert res.status_code == 302
    assert fetched_user.email == "mariobrown@gmail.com"
    assert fetched_user.firstname == "mario"
    assert fetched_user.lastname == "brown"
    assert fetched_user.dateofbirth == datetime(1995, 12, 31)
    assert urlparse(res.location).path == "/"
