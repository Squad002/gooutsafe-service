from .fixtures import app, client, db
from . import helpers


def test_me_view_is_available_for_user(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/me")

    assert res.status_code == 200


def test_me_view_is_available_for_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/me")

    assert res.status_code == 200


def test_me_view_is_correct_for_user(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/me")

    assert b"mariobrown@gmail.com" in res.data
    assert b"mario" in res.data
    assert b"brown" in res.data
    assert b"RSSMRA95T31H501R" in res.data


def test_me_view_is_correct_for_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.get("/me")

    assert b"giuseppebrown@lalocanda.com" in res.data
    assert b"giuseppe" in res.data
    assert b"yellow" in res.data
    assert b"YLLGPP63A01B519O" in res.data


def test_me_view_not_available_for_unlogged_users(client):

    res = client.get("/me")

    assert res.status_code == 401


def test_me_view_redirects_authority(client):
    helpers.create_health_authority(client)
    helpers.login_authority(client)

    res = client.get("/me")

    assert res.status_code == 302


def test_profile_forms_are_available(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res1 = client.get("/me/change_password")
    res2 = client.get("/me/change_anagraphic")
    res3 = client.get("/me/change_contacts")

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 200

# ! BUG
# Questo chiama su LoginUser (che sarebbe current_user) verify_password() che non esiste più, ma bisogna eseguire il metodo
# users.login() in cartella /api (come viene fatto sulla registrazione utente) 
def test_password_form(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.post(
        "/me/change_password",
        data=dict(
            new_password="5678",
            password_confirm="5678",
            old_password="1234",
        ),
        follow_redirects=False,
    )

    assert res.status_code == 200

    helpers.logout

    res = client.post(
        "/login/user",
        data=dict(
            email="mariobrown@gmail.com",
            password="5678",
        ),
        follow_redirects=False,
    )
    assert res.status_code == 302


def test_anagraphic_form_user(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.post(
        "/me/change_anagraphic",
        data=dict(
            firstname="Hattori",
            lastname="Hanzo",
            fiscalcode="HTTHNZ45B02D612A",
            dateofbirth="1945-02-02",
            password="1234",
        ),
        follow_redirects=False,
    )

    assert res.status_code == 200

    res = client.get("/me")
    assert b"Hattori" in res.data
    assert b"Hanzo" in res.data
    assert b"HTTHNZ45B02D612A" in res.data


def test_anagraphic_form_operator(client):
    helpers.create_operator(client)
    helpers.login_operator(client)

    res = client.post(
        "/me/change_anagraphic",
        data=dict(
            firstname="O-Ren",
            lastname="Ishii",
            fiscalcode="RNXSHX74C03D612A",
            # TODO add patch for birthdate to user service api
            dateofbirth="1945-03-03",
            password="5678",
        ),
        follow_redirects=False,
    )

    assert res.status_code == 200

    res = client.get("/me")
    assert b"O-Ren" in res.data
    assert b"Ishii" in res.data
    assert b"RNXSHX74C03D612A" in res.data


def test_contact_form(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.post(
        "/me/change_contacts",
        data=dict(
            email="hattori@katanas.jp",
            phonenumber="+81855696969",
            password="1234",
        ),
        follow_redirects=False,
    )

    assert res.status_code == 200

    res = client.get("/me")
    assert b"hattori@katanas.jp" in res.data


def test_wrong_password_in_forms(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res1 = client.post(
        "/me/change_password",
        data=dict(
            new_password="PaiMei",
            password_confirm="PaiMei",
            old_password="Budd",
        ),
        follow_redirects=False,
    )

    res2 = client.post(
        "/me/change_anagraphic",
        data=dict(
            firstname="Hattori",
            lastname="Hanzo",
            fiscalcode="HTTHNZ45B02D612A",
            dateofbirth="1945-02-02",
            password="BeatrixKiddo",
        ),
        follow_redirects=False,
    )

    res3 = client.post(
        "/me/change_contacts",
        data=dict(
            email="hattori@katanas.jp",
            phonenumber="+81855696969",
            password="ElleDriver",
        ),
        follow_redirects=False,
    )

    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 200


def test_form_iframes_in_view(client):
    helpers.create_user(client)
    helpers.login_user(client)

    res = client.get("/me")

    assert b"password_iframe" in res.data
    assert b"anagraphic_iframe" in res.data
    assert b"contacts_iframe" in res.data
