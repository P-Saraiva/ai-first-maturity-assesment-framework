"""
Application configuration utilities for AFS Assessment Framework

This module provides utilities for loading and validating application configuration.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any


class ConfigValidator:
    """Validates application configuration"""
    
    @staticmethod
    def validate_database_config(app) -> bool:
        """
        Validate database configuration
        
        Args:
            app: Flask application instance
            
        Returns:
            bool: True if configuration is valid
        """
        required_keys = ['SQLALCHEMY_DATABASE_URI']
        
        for key in required_keys:
            if not app.config.get(key):
                app.logger.error(f"Missing required database configuration: {key}")
                return False
        
        # Test database connection if possible
        try:
            from .extensions import db
            with app.app_context():
                from sqlalchemy import text
                db.engine.execute(text('SELECT 1'))
            app.logger.info("Database connection test successful")
            return True
        except Exception as e:
            app.logger.warning(f"Database connection test failed: {str(e)}")
            return True  # Don't fail startup on connection test failure
    
    @staticmethod
    def validate_security_config(app) -> bool:
        """
        Validate security configuration
        
        Args:
            app: Flask application instance
            
        Returns:
            bool: True if configuration is valid
        """
        if not app.config.get('SECRET_KEY'):
            app.logger.error("SECRET_KEY not configured")
            return False
        
        if app.config.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
            if not app.debug:
                app.logger.warning("Using default SECRET_KEY in non-debug mode")
        
        return True
    
    @staticmethod
    def validate_directories(app) -> bool:
        """
        Validate and create required directories
        
        Args:
            app: Flask application instance
            
        Returns:
            bool: True if directories are valid
        """
        directories = [
            app.config.get('UPLOAD_FOLDER', 'static/uploads'),
            app.config.get('EXPORT_FOLDER', 'data/exports'),
            'logs',
            'backups'
        ]
        
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                app.logger.debug(f"Directory ensured: {directory}")
            except Exception as e:
                app.logger.error(f"Failed to create directory {directory}: {str(e)}")
                return False
        
        return True
    
    @staticmethod
    def validate_all(app) -> bool:
        """
        Run all configuration validations
        
        Args:
            app: Flask application instance
            
        Returns:
            bool: True if all validations pass
        """
        validators = [
            ConfigValidator.validate_security_config,
            ConfigValidator.validate_directories,
            ConfigValidator.validate_database_config,
        ]
        
        for validator in validators:
            if not validator(app):
                return False
        
        return True


def setup_logging(app):
    """
    Set up application logging
    
    Args:
        app: Flask application instance
    """
    # Get log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Set up formatter
    formatter = logging.Formatter(
        app.config.get('LOG_FORMAT', 
                      '%(asctime)s %(levelname)s %(name)s %(message)s')
    )
    
    # Configure Flask's logger
    app.logger.setLevel(log_level)
    
    # Add file handler if not in testing mode
    if not app.testing:
        log_file = app.config.get('LOG_FILE', 'logs/app.log')
        
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Set up rotating file handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=app.config.get('LOG_MAX_BYTES', 10485760),
            backupCount=app.config.get('LOG_BACKUP_COUNT', 5)
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)


def load_environment_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables
    
    Returns:
        dict: Environment configuration
    """
    env_config = {}
    
    # Load specific environment variables
    env_vars = [
        'FLASK_ENV', 'SECRET_KEY', 'DATABASE_URL', 'REDIS_URL',
        'LOG_LEVEL', 'CACHE_TYPE', 'DEBUG'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value is not None:
            env_config[var] = value
    
    return env_config


__all__ = ['ConfigValidator', 'setup_logging', 'load_environment_config']