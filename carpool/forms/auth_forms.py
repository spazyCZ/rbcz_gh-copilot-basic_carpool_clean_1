"""
Authentication forms for login and registration.

This module defines Flask-WTF forms for user authentication including
login, registration, and password management forms.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from carpool.models.user import User


class LoginForm(FlaskForm):
    """
    Login form for user authentication.
    
    Provides fields for username/email and password with validation.
    """
    
    username = StringField(
        'Username or Email',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Enter your username or email', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your password', 'class': 'form-control'}
    )
    
    remember_me = BooleanField(
        'Remember Me',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Sign In',
        render_kw={'class': 'btn btn-primary'}
    )


class RegisterForm(FlaskForm):
    """
    Registration form for new user accounts.
    
    Provides fields for username, email, password, and password confirmation with validation.
    """
    
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Choose a username', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'placeholder': 'Enter your email address', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={'placeholder': 'Create a password (min 6 characters)', 'class': 'form-control'}
    )
    
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your password', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Register',
        render_kw={'class': 'btn btn-success'}
    )
    
    def validate_username(self, username):
        """
        Custom validation for username uniqueness.
        
        :param username: Username field to validate
        :raises ValidationError: If username already exists
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validation for email uniqueness.
        
        :param email: Email field to validate
        :raises ValidationError: If email already exists
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class ChangePasswordForm(FlaskForm):
    """
    Form for changing user password.
    
    Provides fields for current password, new password, and confirmation.
    """
    
    current_password = PasswordField(
        'Current Password',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Enter your current password', 'class': 'form-control'}
    )
    
    new_password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={'placeholder': 'Enter new password (min 6 characters)', 'class': 'form-control'}
    )
    
    new_password_confirm = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your new password', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Change Password',
        render_kw={'class': 'btn btn-warning'}
    )


class ForgotPasswordForm(FlaskForm):
    """
    Form for password reset requests.
    
    Provides email field for password reset functionality.
    """
    
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'placeholder': 'Enter your email address', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Send Reset Instructions',
        render_kw={'class': 'btn btn-warning'}
    )


class AdminCreateUserForm(FlaskForm):
    """
    Admin form for creating new user accounts.
    
    Provides fields for username, email, password, and role selection.
    """
    
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Enter username', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'placeholder': 'Enter email address', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={'placeholder': 'Set password (min 6 characters)', 'class': 'form-control'}
    )
    
    role = SelectField(
        'Role',
        choices=[
            ('user', 'User'),
            ('administrator', 'Administrator'),
            ('guest', 'Guest')
        ],
        default='user',
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Create User',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_username(self, username):
        """
        Custom validation for username uniqueness.
        
        :param username: Username field to validate
        :raises ValidationError: If username already exists
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validation for email uniqueness.
        
        :param email: Email field to validate
        :raises ValidationError: If email already exists
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class AdminEditUserForm(FlaskForm):
    """
    Admin form for editing existing user accounts.
    
    Provides fields for email and role changes.
    """
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'class': 'form-control'}
    )
    
    role = SelectField(
        'Role',
        choices=[
            ('user', 'User'),
            ('administrator', 'Administrator'),
            ('guest', 'Guest')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Update User',
        render_kw={'class': 'btn btn-warning'}
    )
    
    def __init__(self, original_email, *args, **kwargs):
        """
        Initialize form with original email for validation.
        
        :param original_email: Original email address of the user being edited
        """
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """
        Custom validation for email uniqueness (excluding current user).
        
        :param email: Email field to validate
        :raises ValidationError: If email already exists for another user
        """
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')
