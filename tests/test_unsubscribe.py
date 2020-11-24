from urllib.parse import urlparse
from datetime import date
from flask import session

from .fixtures import app, client, db
from . import helpers
from monolith.models import User


def test_unsubscribe_view_is_available(client):

    res = client.get("/unsubscribe")

    assert res.status_code == 302
