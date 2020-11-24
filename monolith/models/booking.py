from monolith import db
from sqlalchemy.orm import relationship


class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=False)
    user = relationship("User", back_populates="booking")

    table_id = db.Column(db.Integer, db.ForeignKey("table.id"), primary_key=False)
    table = relationship("Table", back_populates="booking")

    booking_number = db.Column(db.Integer, nullable=False)

    start_booking = db.Column(db.DateTime, nullable=False)
    end_booking = db.Column(db.DateTime, nullable=False)
    confirmed_booking = db.Column(db.Boolean, default=False)
    checkin = db.Column(db.Boolean, default=False)

    def user_already_booked(self, id):
        user_list = list(
            db.session.query(Booking.user_id)
            .filter_by(booking_number=self.booking_number)
            .all()
        )

        id_user_list = []
        for user in user_list:
            id_user = user[0]
            id_user_list.append(id_user)

        return id in id_user_list
