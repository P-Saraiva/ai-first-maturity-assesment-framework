"""
Models Module for AFS Assessment Framework

This module exports all SQLAlchemy models and provides utilities
for model management and database operations.
"""

from .base import Base, BaseModel, TimestampMixin, SoftDeleteMixin
from .question import Section, Area, Question
from .assessment import Assessment, AssessmentStatus
from .response import Response
from .progression import MaturityProgression

# Import database utilities
from .database import (
    DatabaseAdapter, 
    DatabaseFactory, 
    get_database_adapter,
    H2Adapter,
    PostgreSQLAdapter,
    MySQLAdapter
)
from .database_manager import DatabaseManager, get_db_adapter, init_database_with_app

# Export all models
__all__ = [
    # Base classes
    'Base',
    'BaseModel', 
    'TimestampMixin',
    'SoftDeleteMixin',
    
    # Core models
    'Section',
    'Area',
    'Question',
    'Assessment',
    'AssessmentStatus',
    'Response',
    'MaturityProgression',
    
    # Database adapters
    'DatabaseAdapter',
    'DatabaseFactory',
    'get_database_adapter', 
    'H2Adapter',
    'PostgreSQLAdapter',
    'MySQLAdapter',
    
    # Database management
    'DatabaseManager',
    'get_db_adapter',
    'init_database_with_app'
]


def get_all_models():
    """
    Get all model classes
    
    Returns:
        List of model classes
    """
    return [
        Section,
        Area,
        Question, 
        Assessment,
        Response
    ]


def create_all_tables(engine):
    """
    Create all tables in the database
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """
    Drop all tables from the database
    
    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.drop_all(engine)