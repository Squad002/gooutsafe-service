from .fixtures import app, client, db
from . import helpers


# TODO access only a single user!
def test_health_authority_can_access_users(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    res = get_response_from_users(client)

    # TODO check the list of the users
    assert res.status_code == 200


def test_user_cannot_access_users(client):
    helpers.create_user(client)
    helpers.login_user(client)
    res = get_response_from_users(client)

    assert res.status_code == 401


def test_operator_cannot_access_users(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    res = get_response_from_users(client)

    assert res.status_code == 401


# They will still find a way
def test_anonymous_cannot_access_users(client):
    res = get_response_from_users(client)

    assert res.status_code == 302


def get_response_from_users(client):
    return client.get(
        "/users",
        follow_redirects=False,
    )
