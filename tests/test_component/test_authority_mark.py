from ..fixtures import app, client
from .. import helpers
from monolith.models import User, Mark
from monolith.api.users import get_user_by_id

def test_ha_should_access_own_new_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get(
        "/marks/new",
        follow_redirects=False,
    )

    assert res.status_code == 200


def test_ha_should_mark_one_user_through_ssn_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    res = client.post(
        "/marks/new",
        data={"identifier": helpers.user2["fiscalcode"], "duration": 15},
        follow_redirects=False,
    )

    assert res.status_code == 302
    
    user = get_user_by_id(1)
    assert user["marked"]


def test_ha_should_not_work_with_a_ssn_not_in_db(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    res = client.post(
        "/marks/new",
        data={"identifier": "wrong_fiscal_code", "duration": 15},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"User not found." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_string_duration(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["fiscalcode"], "duration": "sf"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"This field must be a number." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_less_than_one(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["fiscalcode"], "duration": -4},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_more_than_sixty(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)
    
    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["fiscalcode"], "duration": 104},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_operator_should_not_access_new_mark_page(client):
    helpers.create_operator(client)
    helpers.login_operator(client)
    helpers.create_user(client)

    res = client.get(
        "marks/new",
        follow_redirects=False,
    )

    assert res.status_code == 401


def test_user_should_not_access_new_mark_page(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get(
        "marks/new",
        follow_redirects=False,
    )

    assert res.status_code == 401


# They will still find a way
def test_anonymous_should_not_access_new_mark_page(client):
    res = client.get(
        "marks/new",
        follow_redirects=False,
    )

    assert res.status_code == 302


# Test on Email view


def test_ha_should_mark_one_user_on_email_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["email"], "duration": 15},
        follow_redirects=False,
    )

    user = get_user_by_id(1)

    assert user["marked"]
    assert res.status_code == 302


def test_ha_should_not_work_with_a_email_not_in_db_on_email_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    res = client.post(
        "/marks/new",
        data={"identifier": "wrong_email@mail.com", "duration": 15},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"User not found." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_string_duration_on_email_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    helpers.create_user(client)
    user = get_user_by_id(1)

    res = client.post(
        "/marks/new",
        data={"identifier": user["email"], "duration": "sf"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"This field must be a number." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_less_than_one_on_email_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["email"], "duration": -4},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_more_than_sixty_on_email_mark_page(
    client
):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["email"], "duration": 104},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


# Test on Phonenumber view


def test_ha_should_mark_one_user_on_phone_number_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["phonenumber"], "duration": 15},
        follow_redirects=False,
    )

    user = get_user_by_id(1)
    assert user["marked"] == True
    assert res.status_code == 302


def test_ha_should_not_work_with_a_phone_number_not_in_db_on_phone_number_mark_page(
    client
):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    res = client.post(
        "/marks/new",
        data={"identifier": "wrong_phone_number", "duration": 15},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"User not found." in res.data

    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_string_duration_on_phone_number_mark_page(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["phonenumber"], "duration": "sf"},
        follow_redirects=True,
    )

    assert res.status_code == 200
    assert b"This field must be a number." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_less_than_one_on_phone_number_mark_page(
    client
):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)

    user = get_user_by_id(1)
    res = client.post(
        "/marks/new",
        data={"identifier": user["phonenumber"], "duration": -4},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data
    user = get_user_by_id(1)
    assert not user["marked"]


def test_ha_should_not_work_with_duration_more_than_sixty_on_phone_number_mark_page(
    client
):
    helpers.create_health_authority(client)
    helpers.login_authority(client)
    helpers.create_user(client)
    user = get_user_by_id(1)

    res = client.post(
        "/marks/new",
        data={"identifier": user["phonenumber"], "duration": 104},
        follow_redirects=False,
    )

    assert res.status_code == 200
    assert b"The duration must be between 1 and 60." in res.data

    user = get_user_by_id(1)
    assert not user["marked"]


# Helpers


def are_marks_empty(db):
    return len(db.session.query(Mark).all()) == 0
