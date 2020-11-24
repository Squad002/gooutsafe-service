from monolith import db
from .abstract_user import AbstractUser


class Operator(AbstractUser):
    __tablename__ = "operator"
    restaurants = db.relationship("Restaurant", backref="operator")

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password_hash = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    phonenumber = db.Column(db.Unicode(40))
    fiscalcode = db.Column(db.Unicode(128))

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
