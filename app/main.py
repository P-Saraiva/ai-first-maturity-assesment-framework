"""
Main application entry point for AFS Assessment Framework

This module provides the main application entry point and basic health checks.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import jsonify, request
from app import create_app
from app.extensions import db


def create_application():
    """
    Create and configure the Flask application
    
    Returns:
        Flask: Configured application instance
    """
    app = create_app()
    
    # Add health check endpoints
    @app.route('/health')
    def health_check():
        """Basic health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'AFS Assessment Framework',
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('CONFIG_NAME', 'unknown')
        })
    
    @app.route('/health/detailed')
    def detailed_health_check():
        """Detailed health check with component status"""
        health_data = {
            'status': 'healthy',
            'service': 'AFS Assessment Framework',
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('CONFIG_NAME', 'unknown'),
            'components': {}
        }
        
        # Check database connection
        try:
            with app.app_context():
                from sqlalchemy import text
                db.engine.execute(text('SELECT 1'))
            health_data['components']['database'] = 'healthy'
        except Exception as e:
            health_data['components']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'degraded'
        
        # Check cache if configured
        try:
            from app.extensions import cache
            cache.get('health_check')
            health_data['components']['cache'] = 'healthy'
        except Exception as e:
            health_data['components']['cache'] = f'unavailable: {str(e)}'
        
        return jsonify(health_data)
    
    @app.route('/version')
    def version_info():
        """Version information endpoint"""
        return jsonify({
            'version': app.config.get('VERSION', '1.0.0'),
            'build': app.config.get('BUILD_NUMBER', 'unknown'),
            'environment': app.config.get('CONFIG_NAME', 'unknown'),
            'python_version': sys.version
        })
    
    return app


# Create application instance
app = create_application()


if __name__ == '__main__':
    """
    Development server entry point
    """
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    print(f"Starting AFS Assessment Framework on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {app.config.get('CONFIG_NAME', 'unknown')}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )


__all__ = ['create_application', 'app']