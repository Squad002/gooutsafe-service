from monolith import db


class Table(db.Model):
    __tablename__ = "table"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text(100))
    seats = db.Column(db.Integer)

    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))

    restaurant = db.relationship("Restaurant", back_populates="tables")
    booking = db.relationship("Booking", back_populates="table")
