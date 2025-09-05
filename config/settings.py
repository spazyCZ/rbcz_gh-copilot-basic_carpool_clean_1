"""
Configuration classes for the Flask parking reservation application.

This module provides configuration classes for different environments
(Development, Testing, Production) that read from environment variables.
"""
import os
from typing import Optional


class Config:
    """
    Base configuration class with common settings.
    
    All configuration values are read from environment variables with
    sensible defaults for development.
    """
    
    # Flask Core Settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL', 'sqlite:///parking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '5')),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '20')),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', '3600'))
    }
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security Settings
    SESSION_COOKIE_SECURE: bool = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY: bool = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    
    # CSRF Protection
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_SESSION_KEY: str = os.environ.get('CSRF_SESSION_KEY', 'csrf_token_key')
    
    # Rate Limiting
    RATELIMIT_DEFAULT: str = os.environ.get('RATE_LIMIT', '100/hour')
    RATELIMIT_STORAGE_URL: str = 'memory://'
    
    # Admin User Defaults
    ADMIN_DEFAULT_USERNAME: str = os.environ.get('ADMIN_DEFAULT_USERNAME', 'admin')
    ADMIN_DEFAULT_EMAIL: str = os.environ.get('ADMIN_DEFAULT_EMAIL', 'admin@example.com')
    ADMIN_DEFAULT_PASSWORD: str = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
    
    # Optional Features
    ENABLE_SENTRY: bool = os.environ.get('ENABLE_SENTRY', 'False').lower() == 'true'
    SENTRY_DSN: Optional[str] = os.environ.get('SENTRY_DSN')


class DevelopmentConfig(Config):
    """
    Development configuration with debug mode enabled and relaxed security.
    """
    DEBUG: bool = True
    TESTING: bool = False
    
    # Development-specific database (in-memory for faster iteration)
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL', 'sqlite:///dev_parking.db')
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE: bool = False
    WTF_CSRF_ENABLED: bool = False  # Disable CSRF for easier API testing
    
    # More verbose logging for development
    LOG_LEVEL: str = 'DEBUG'


class TestingConfig(Config):
    """
    Testing configuration with in-memory database and disabled features.
    """
    DEBUG: bool = False
    TESTING: bool = True
    
    # In-memory database for fast, isolated tests
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
    
    # Disable security features that interfere with testing
    WTF_CSRF_ENABLED: bool = False
    SESSION_COOKIE_SECURE: bool = False
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED: bool = False
    
    # Test-specific admin credentials
    ADMIN_DEFAULT_USERNAME: str = 'test_admin'
    ADMIN_DEFAULT_EMAIL: str = 'test@example.com'
    ADMIN_DEFAULT_PASSWORD: str = 'test123'


class ProductionConfig(Config):
    """
    Production configuration with enhanced security and performance settings.
    """
    DEBUG: bool = False
    TESTING: bool = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    WTF_CSRF_ENABLED: bool = True
    
    # Production database (should be PostgreSQL)
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/parking_prod')
    
    # Production logging
    LOG_LEVEL: str = 'WARNING'
    
    # Enable optional production features
    ENABLE_SENTRY: bool = True


# Configuration mapping for easy selection
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration class by name.
    
    :param config_name: Configuration name ('development', 'testing', 'production')
    :return: Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config_by_name.get(config_name, DevelopmentConfig)
    return config_class()