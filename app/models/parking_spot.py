from app.extensions import db


class ParkingSpot(db.Model):
    id = db.Column(db.String, primary_key=True)
    status = db.Column(db.String, default="free")
    location = db.Column(db.String, nullable=True)

    reservations = db.relationship("Reservation", back_populates="spot", cascade="all, delete-orphan")
