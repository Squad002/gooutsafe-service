from monolith import db
from sqlalchemy.orm import relationship


class RestaurantsPrecautions(db.Model):
    __tablename__ = "restaurants_precautions"

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), primary_key=True
    )
    restaurant = relationship(
        "Restaurant", foreign_keys="RestaurantsPrecautions.restaurant_id"
    )

    precautions_id = db.Column(
        db.Integer, db.ForeignKey("precautions.id"), primary_key=True
    )
    precautions = relationship(
        "Precautions", foreign_keys="RestaurantsPrecautions.precautions_id"
    )
