from ..fixtures import db, app
from .. import helpers

from monolith.models.mark import Mark
from datetime import datetime


def test_mark_should_create_mark_association(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user)
    db.session.commit()

    mark = db.session.query(Mark).filter(Mark.authority_id == ha.id).first()

    assert mark.user_id == user.id
    assert mark.duration == 14
    assert mark.created.date() == datetime.utcnow().date()


def test_mark_should_create_mark_association_with_custom_duration(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, duration=18)
    db.session.commit()

    mark = db.session.query(Mark).filter(Mark.authority_id == ha.id).first()

    assert mark.user_id == user.id
    assert mark.duration == 18
    assert mark.created.date() == datetime.utcnow().date()


def test_mark_should_create_mark_association_with_custom_starting_date(db):
    ha = helpers.insert_health_authority(db)
    user = helpers.insert_user(db)
    ha.mark(user, starting_date=datetime(2020, 10, 15))
    db.session.commit()

    mark = db.session.query(Mark).filter(Mark.authority_id == ha.id).first()

    assert mark.user_id == user.id
    assert mark.duration == 14
    assert mark.created.date() == datetime(2020, 10, 15).date()
