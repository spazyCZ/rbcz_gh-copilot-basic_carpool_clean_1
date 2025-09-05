from app.extensions import db


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.String, db.ForeignKey('parking_spot.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)

    spot = db.relationship('ParkingSpot', back_populates='reservations')

    __table_args__ = (db.UniqueConstraint('spot_id', 'reservation_date', name='uix_spot_date'),)
