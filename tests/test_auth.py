from .fixtures import app, client, db
from . import helpers

# 140 - 42 132.75
# 115 - 67
# 139 - 43
# TODO ERROR in breakers: list index out of range
def test_user_correct_login(client):
    helpers.create_user(client)
    res = helpers.login_user(client)

    assert res.status_code == 302


def test_operator_correct_login(client):
    helpers.create_operator(client)
    res = helpers.login_operator(client)

    assert res.status_code == 302


def test_health_authority_correct_login(client):
    helpers.create_health_authority(client)
    res = helpers.login_authority(client)

    assert res.status_code == 302
