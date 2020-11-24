from monolith import db
from .timestamp_mixin import TimestampMixin


class Mark(TimestampMixin, db.Model):
    __tablename__ = "mark"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    authority_id = db.Column(
        db.Integer, db.ForeignKey("authority.id"), primary_key=True
    )

    authority = db.relationship("HealthAuthority", back_populates="marks")
    user = db.relationship("User", back_populates="marks")

    duration = db.Column(db.Integer, default=14)
