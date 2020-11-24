from monolith import db
from .timestamp_mixin import TimestampMixin


class Review(TimestampMixin, db.Model):
    __tablename__ = "review"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), primary_key=True
    )

    restaurant = db.relationship("Restaurant", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    rating = db.Column(db.SmallInteger, nullable=False)
    message = db.Column(db.UnicodeText)
