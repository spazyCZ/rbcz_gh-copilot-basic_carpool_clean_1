"""
Configuration settings for the Carpool application.
This module defines different configuration classes for various environments.
"""
import os
from datetime import timedelta

class Config:
    """
    Base configuration class with settings common to all environments.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-me-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///carpool.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    
    # Security headers
    SECURITY_HEADERS = {
        'Content-Security-Policy': {
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' cdn.jsdelivr.net",
            'style-src': "'self' 'unsafe-inline' cdn.jsdelivr.net",
            'font-src': "'self' cdn.jsdelivr.net",
        }
    }

class DevelopmentConfig(Config):
    """
    Development environment configuration.
    """
    DEBUG = True
    TESTING = False
    
    # Disable security headers in development
    SECURITY_HEADERS = None

class TestingConfig(Config):
    """
    Testing environment configuration.
    """
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Disable security headers in testing
    SECURITY_HEADERS = None

class ProductionConfig(Config):
    """
    Production environment configuration.
    """
    DEBUG = False
    TESTING = False
    
    # Force HTTPS in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

# Dictionary for easy access to different configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
