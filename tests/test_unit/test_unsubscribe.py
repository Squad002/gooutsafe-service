from monolith.views.auth import unsubscribe
from tests.helpers import login_user
from monolith.models.review import Review
from ..fixtures import db, app, client
from flask import session
from flask_login import current_user
from monolith.models import User, Operator


from .. import helpers

from datetime import datetime, timedelta


def test_user_has_been_deleted_should_be_true(client, db):

    helpers.create_user(client)
    helpers.login_user(client)

    helpers.unsubscribe(client)

    user = db.session.query(User).filter(User.email == "deleted@deleted.it").first()

    assert user.firstname == "deleted"


def test_operator_has_been_deleted_should_be_true(client, db):

    helpers.create_operator(client)
    helpers.login_operator(client)

    helpers.unsubscribe(client)

    user = (
        db.session.query(Operator)
        .filter(Operator.email == "deleted@deleted.it")
        .first()
    )

    assert user.firstname == "deleted"


def test_marked_user_cannot_be_deleted_should_be_true(client, db):

    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, duration=18)
    db.session.commit()

    helpers.login_user(client)
    helpers.unsubscribe(client)

    user = db.session.query(User).filter(User.email == "mariobrown@gmail.com").first()

    assert user.firstname == "mario"
