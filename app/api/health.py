"""
Health check API endpoint.

Provides system health and database connectivity status.
"""
from flask import jsonify, current_app
from datetime import datetime

from app.api import api_bp
from app.extensions import db


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Get application health status.
    
    Returns system status, database connectivity, and timestamp.
    Used for monitoring and load balancer health checks.
    
    :return: JSON response with health status
    """
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
        db_error = None
    except Exception as e:
        db_status = 'unhealthy'
        db_error = str(e)
        current_app.logger.error(f"Database health check failed: {e}")
    
    # Determine overall status
    overall_status = 'healthy' if db_status == 'healthy' else 'unhealthy'
    
    health_data = {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',  # Could be read from config or version file
        'database': {
            'status': db_status,
            'error': db_error
        },
        'services': {
            'api': 'healthy',
            'authentication': 'healthy'
        }
    }
    
    # Return appropriate HTTP status code
    status_code = 200 if overall_status == 'healthy' else 503
    
    return jsonify({
        'data': health_data
    }), status_code