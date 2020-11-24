from monolith import db
from monolith.models.searchable_mixin import SearchableMixin
from .table import Table
import enum
import datetime

# precautions = db.Table('precautions',
#     db.Column('precaution_id', db.Integer, db.ForeignKey('precaution.id'), primary_key=True),
#     db.Column('restaurant', db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
# )


class CuisineType(enum.Enum):
    ETHNIC = "Ethnic"
    FAST_FOOD = "Fast Food"
    PUB = "Pub"

    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]


class Restaurant(SearchableMixin, db.Model):
    __tablename__ = "restaurant"
    __searchable__ = ["name", "phonenumber", "average_rating"]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text(100))

    lat = db.Column(db.Float)  # restaurant latitude
    lon = db.Column(db.Float)  # restaurant longitude

    phonenumber = db.Column(db.Unicode(40))
    time_of_stay = db.Column(db.Integer)  # minutes
    cuisine_type = db.Column(db.Enum(CuisineType))
    opening_hours = db.Column(db.Integer)
    closing_hours = db.Column(db.Integer)
    operator_id = db.Column(db.Integer, db.ForeignKey("operator.id"))
    average_rating = db.Column(db.Integer, default=0)

    # precautions = db.relationship("Precaution", secondary=precautions, backref="restaurants")
    tables = db.relationship("Table", back_populates="restaurant")
    reviews = db.relationship("Review", back_populates="restaurant")
    menus = db.relationship("Menu", back_populates="restaurant")

    def get_bookings(self, starting_booking_datetime: datetime):
        """Get all the bookings that were confirmed starting from a specific time.

        Args:
            starting_booking_time (datetime): the starting time of the booking
        """
        total_real_bookings = []
        for table in self.tables:
            bookings = [
                b
                for b in table.booking
                if b.checkin and b.start_booking == starting_booking_datetime
            ]
            total_real_bookings.extend(bookings)

        return total_real_bookings

    def get_free_table(self, seats, date_hour):
        filtered_tables = []
        tables_list = Table.query.filter_by(restaurant_id=self.id).order_by(
            Table.seats.asc()
        )
        for table in tables_list:
            if table.seats >= seats:
                filtered_tables.append(table)

        id_booked_tables = []
        for table in filtered_tables:
            for booking in table.booking:
                if booking.start_booking == date_hour:
                    id_booked_tables.append(table.id)
                    break

        for table in filtered_tables:
            if table.id not in id_booked_tables:
                return table.id
        return None
