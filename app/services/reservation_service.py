from datetime import date
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Reservation


def list_reservations():
    return Reservation.query.all()


def create_reservation(spot_id: str, name: str, reservation_date: date) -> Reservation:
    reservation = Reservation(spot_id=spot_id, name=name, reservation_date=reservation_date)
    db.session.add(reservation)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Spot already reserved for this date")
    return reservation
