#!/usr/bin/env python3
"""
Application entry point for the parking reservation system.

This script creates and runs the Flask application using the
application factory pattern.
"""
import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode
    )