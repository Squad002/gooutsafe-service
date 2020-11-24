from monolith import db


class Precautions(db.Model):
    __tablename__ = "precautions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text(100))
