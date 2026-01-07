"""
Development configuration for AFS Assessment Framework
"""

from .base import Config


class DevelopmentConfig(Config):
    """Development configuration with debug settings"""
    
    DEBUG = True
    TESTING = False
    
    # Database settings for development
    # Use the same SQLite file as setup_database.py (under instance/)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app_dev.db'
    SQLALCHEMY_ECHO = True  # Log all SQL queries
    
    # Cache settings for development
    CACHE_TYPE = 'simple'
    
    # Security settings (relaxed for development)
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = False
    
    # Logging settings for development
    LOG_LEVEL = 'DEBUG'

    # Active sections for development (limit to new AI Security structure)
    ACTIVE_SECTION_IDS = 'ETSI,GSA,IAA,DPR,PUT,TSA,QEI'
    
    # Feature flags for development
    ENABLE_REGISTRATION = True
    ENABLE_API = True
    ENABLE_EXPORTS = True
    ENABLE_ANALYTICS = True
    
    # Development-specific settings
    ASSETS_DEBUG = True
    COMPRESSOR_DEBUG = True
    
    @staticmethod
    def init_app(app):
        """Initialize development-specific settings"""
        Config.init_app(app)
        
        # Additional development initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Enable Flask-DebugToolbar if available
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension()
            toolbar.init_app(app)
        except ImportError:
            pass