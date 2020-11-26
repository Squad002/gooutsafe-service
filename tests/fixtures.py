from monolith import create_app, db as dba
from monolith.services.auth import login_manager

import pytest
import os
import requests


@pytest.yield_fixture
def app(testrun_uid):
    app = create_app(
        config_name="testing",
        updated_variables={
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///gooutsafe_test_{testrun_uid}.db"
        },
    )
    db_path = os.path.join(app.root_path, f"gooutsafe_test_{testrun_uid}.db")

    yield app

    # Teardown of the DB
    dba.session.remove()
    dba.drop_all(app=app)
    os.unlink(db_path)

    # Teardown DBs on the microservices
    res = requests.delete("http://localhost:5001/testing/services/user/db")
    requests.delete("http://localhost:5002/testing/services/booking/db")
    requests.delete("http://localhost:5003/testing/services/restaurant/db")

    

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.yield_fixture
def db(app):
    yield dba
