from app.extensions import db
from app.models import ParkingSpot


def list_spots():
    return ParkingSpot.query.all()


def create_spot(spot_id: str, status: str = 'free', location: str | None = None) -> ParkingSpot:
    spot = ParkingSpot(id=spot_id, status=status, location=location)
    db.session.add(spot)
    db.session.commit()
    return spot
