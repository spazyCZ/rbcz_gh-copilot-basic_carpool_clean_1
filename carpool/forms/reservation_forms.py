"""
Reservation forms for parking spot reservations.

This module defines Flask-WTF forms for creating and editing parking reservations.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime, date
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation


class ReservationForm(FlaskForm):
    """
    Form for creating new parking reservations.
    
    Provides fields for name, parking spot selection, and date selection.
    """
    
    name = StringField(
        'Reservation Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter name for reservation', 'class': 'form-control'}
    )
    
    spot_id = SelectField(
        'Parking Spot',
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    reservation_date = DateField(
        'Reservation Date',
        validators=[DataRequired()],
        render_kw={'class': 'form-control', 'min': datetime.now().strftime('%Y-%m-%d')}
    )
    
    submit = SubmitField(
        'Make Reservation',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form and populate parking spot choices.
        """
        super(ReservationForm, self).__init__(*args, **kwargs)
        
        # Get available parking spots
        spots = ParkingSpot.query.filter_by(status='available').order_by(ParkingSpot.id).all()
        self.spot_id.choices = [(spot.id, f"{spot.id} - {spot.location}") for spot in spots]
        
        if not self.spot_id.choices:
            self.spot_id.choices = [('', 'No available spots')]
    
    def validate_reservation_date(self, reservation_date):
        """
        Custom validation for reservation date.
        
        :param reservation_date: Date field to validate
        :raises ValidationError: If date is in the past
        """
        if reservation_date.data < date.today():
            raise ValidationError('Reservation date cannot be in the past.')
    
    def validate_spot_id(self, spot_id):
        """
        Custom validation for parking spot availability.
        
        :param spot_id: Spot ID field to validate
        :raises ValidationError: If spot is not available or doesn't exist
        """
        if spot_id.data:
            spot = ParkingSpot.query.get(spot_id.data)
            if not spot:
                raise ValidationError('Selected parking spot does not exist.')
            if not spot.is_available():
                raise ValidationError('Selected parking spot is not available.')
    
    def validate(self, extra_validators=None):
        """
        Custom form validation to check for double booking.
        
        :param extra_validators: Additional validators
        :return: True if validation passes, False otherwise
        """
        if not super(ReservationForm, self).validate(extra_validators):
            return False
        
        # Check for double booking
        if self.spot_id.data and self.reservation_date.data:
            if Reservation.check_double_booking(self.spot_id.data, self.reservation_date.data):
                self.spot_id.errors.append('This parking spot is already reserved for the selected date.')
                return False
        
        return True


class EditReservationForm(FlaskForm):
    """
    Form for editing existing parking reservations.
    
    Provides fields for updating name, parking spot, and date.
    """
    
    name = StringField(
        'Reservation Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Enter name for reservation', 'class': 'form-control'}
    )
    
    spot_id = SelectField(
        'Parking Spot',
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    reservation_date = DateField(
        'Reservation Date',
        validators=[DataRequired()],
        render_kw={'class': 'form-control', 'min': datetime.now().strftime('%Y-%m-%d')}
    )
    
    submit = SubmitField(
        'Update Reservation',
        render_kw={'class': 'btn btn-warning'}
    )
    
    def __init__(self, reservation=None, *args, **kwargs):
        """
        Initialize form with reservation data and populate choices.
        
        :param reservation: Existing reservation to edit
        """
        super(EditReservationForm, self).__init__(*args, **kwargs)
        self.reservation = reservation
        
        # Get available parking spots plus the current spot
        spots = ParkingSpot.query.filter_by(status='available').order_by(ParkingSpot.id).all()
        
        # Add current spot if it's not in the available list
        if reservation and reservation.parking_spot not in spots:
            spots.append(reservation.parking_spot)
            spots.sort(key=lambda x: x.id)
        
        self.spot_id.choices = [(spot.id, f"{spot.id} - {spot.location}") for spot in spots]
        
        if not self.spot_id.choices:
            self.spot_id.choices = [('', 'No available spots')]
        
        # Pre-populate with existing data
        if reservation and not self.data:
            self.name.data = reservation.name
            self.spot_id.data = reservation.spot_id
            self.reservation_date.data = reservation.reservation_date
    
    def validate_reservation_date(self, reservation_date):
        """
        Custom validation for reservation date.
        
        :param reservation_date: Date field to validate
        :raises ValidationError: If date is in the past
        """
        if reservation_date.data < date.today():
            raise ValidationError('Reservation date cannot be in the past.')
    
    def validate_spot_id(self, spot_id):
        """
        Custom validation for parking spot availability.
        
        :param spot_id: Spot ID field to validate
        :raises ValidationError: If spot is not available or doesn't exist
        """
        if spot_id.data:
            spot = ParkingSpot.query.get(spot_id.data)
            if not spot:
                raise ValidationError('Selected parking spot does not exist.')
            
            # Allow current spot or available spots
            if self.reservation:
                if spot_id.data != self.reservation.spot_id and not spot.is_available():
                    raise ValidationError('Selected parking spot is not available.')
            else:
                if not spot.is_available():
                    raise ValidationError('Selected parking spot is not available.')
    
    def validate(self, extra_validators=None):
        """
        Custom form validation to check for double booking.
        
        :param extra_validators: Additional validators
        :return: True if validation passes, False otherwise
        """
        if not super(EditReservationForm, self).validate(extra_validators):
            return False
        
        # Check for double booking (excluding current reservation)
        if self.spot_id.data and self.reservation_date.data and self.reservation:
            exclude_id = self.reservation.id if self.reservation else None
            if Reservation.check_double_booking(self.spot_id.data, self.reservation_date.data, exclude_id):
                self.spot_id.errors.append('This parking spot is already reserved for the selected date.')
                return False
        
        return True


class QuickReservationForm(FlaskForm):
    """
    Simplified form for quick parking reservations.
    
    Provides minimal fields for fast reservation creation.
    """
    
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=2, max=100)],
        render_kw={'placeholder': 'Your name', 'class': 'form-control form-control-sm'}
    )
    
    spot_id = SelectField(
        'Spot',
        validators=[DataRequired()],
        render_kw={'class': 'form-select form-select-sm'}
    )
    
    submit = SubmitField(
        'Reserve Today',
        render_kw={'class': 'btn btn-success btn-sm'}
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form with today's date and available spots.
        """
        super(QuickReservationForm, self).__init__(*args, **kwargs)
        
        # Set today as the reservation date
        self.reservation_date = date.today()
        
        # Get spots available for today
        today = date.today()
        reserved_spots = [r.spot_id for r in Reservation.query.filter_by(reservation_date=today).all()]
        
        available_spots = ParkingSpot.query.filter(
            ParkingSpot.status == 'available',
            ~ParkingSpot.id.in_(reserved_spots)
        ).order_by(ParkingSpot.id).all()
        
        self.spot_id.choices = [(spot.id, spot.id) for spot in available_spots]
        
        if not self.spot_id.choices:
            self.spot_id.choices = [('', 'No spots available')]
    
    def validate_spot_id(self, spot_id):
        """
        Custom validation for parking spot availability today.
        
        :param spot_id: Spot ID field to validate
        :raises ValidationError: If spot is not available today
        """
        if spot_id.data:
            # Check if spot exists and is available
            spot = ParkingSpot.query.get(spot_id.data)
            if not spot or not spot.is_available():
                raise ValidationError('Parking spot is not available.')
            
            # Check if spot is already reserved today
            if Reservation.check_double_booking(spot_id.data, date.today()):
                raise ValidationError('Parking spot is already reserved for today.')
