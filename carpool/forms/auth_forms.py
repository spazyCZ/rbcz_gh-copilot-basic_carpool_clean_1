"""
This module defines forms for user authentication.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from carpool.models.user import User

class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    """
    Form for user registration.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Validate that the username is not already taken.
        
        :param username: Username field
        :raises ValidationError: If username is already taken
        """
        user = User.query.get(username.data)
        if user is not None:
            raise ValidationError('Username already in use. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Validate that the email is not already registered.
        
        :param email: Email field
        :raises ValidationError: If email is already registered
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email address.')

class UserForm(FlaskForm):
    """
    Form for creating or editing users (admin use).
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[Length(min=8)])
    role = SelectField('Role', choices=[
        ('user', 'User'),
        ('administrator', 'Administrator'),
        ('guest', 'Guest')
    ], validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def __init__(self, original_username=None, *args, **kwargs):
        """
        Initialize the UserForm.
        
        :param original_username: Original username when editing a user
        """
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        """
        Validate that the username is not already taken.
        
        :param username: Username field
        :raises ValidationError: If username is already taken by another user
        """
        if self.original_username is None or username.data != self.original_username:
            user = User.query.get(username.data)
            if user is not None:
                raise ValidationError('Username already in use. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Validate that the email is not already registered.
        
        :param email: Email field
        :raises ValidationError: If email is already registered to another user
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None and (self.original_username is None or user.username != self.original_username):
            raise ValidationError('Email already registered. Please use a different email address.')
