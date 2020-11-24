from .fixtures import app, client, db


def test_app_exists(app):
    assert app is not None


def test_app_is_testing_mode(app):
    assert app.config["TESTING"]


def test_app_runs(client):
    res = client.get("/")
    assert res.status_code == 200
