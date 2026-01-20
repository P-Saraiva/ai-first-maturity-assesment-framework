"""
Assessment Model for AFS Assessment Framework

This module defines the Assessment model and related entities for
managing assessment instances and their metadata.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    CheckConstraint, Index, UniqueConstraint, Float
)
from sqlalchemy.orm import relationship, validates

from .base import BaseModel


class AssessmentStatus(Enum):
    """Assessment status enumeration (conceptual)."""
    DRAFT = 'DRAFT'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    LOCKED = 'LOCKED'


class Assessment(BaseModel):
    """
    Assessment model
    
    Represents an assessment instance with metadata and configuration
    """
    
    __tablename__ = 'assessments'
    
    # Basic fields - matching existing database schema
    team_name = Column(String(200), nullable=True)
    
    # Organization and candidate information
    organization_name = Column(String(200), nullable=True)
    account_name = Column(String(200), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Assessor information
    assessor_name = Column(String(200), nullable=True)
    assessor_email = Column(String(200), nullable=True)
    
    # Scoring and results - matching existing schema
    overall_score = Column(Float, nullable=True)
    deviq_classification = Column(String(50), nullable=True)
    completion_date = Column(DateTime, nullable=True)
    results_json = Column(Text, nullable=True)
    
    # Status and timestamps - matching existing schema
    status = Column(String(20), default='IN_PROGRESS', nullable=False)
    
    # Section scores - matching existing schema
    foundational_score = Column(Float, nullable=True)
    transformation_score = Column(Float, nullable=True)
    enterprise_score = Column(Float, nullable=True)
    governance_score = Column(Float, nullable=True)
    
    # Additional metadata - matching existing schema
    assessment_duration_minutes = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    responses = relationship(
        'Response',
        back_populates='assessment',
        cascade='all, delete-orphan'
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'COMPLETED', 'DRAFT', 'LOCKED')",
            name='check_assessment_status'
        ),
        CheckConstraint("overall_score >= 0", name='check_overall_score_positive'),
        CheckConstraint("foundational_score >= 0", name='check_foundational_score_positive'),
        CheckConstraint("transformation_score >= 0", name='check_transformation_score_positive'),
        CheckConstraint("enterprise_score >= 0", name='check_enterprise_score_positive'),
        CheckConstraint("governance_score >= 0", name='check_governance_score_positive'),
        CheckConstraint("assessment_duration_minutes >= 0", name='check_duration_positive'),
        Index('idx_assessments_status', 'status', 'created_at'),
        Index('idx_assessments_team', 'team_name', 'created_at'),
        Index('idx_assessments_completion', 'completion_date'),
        Index('idx_assessments_score', 'overall_score', 'deviq_classification'),
        Index('idx_assessments_team_score', 'team_name', 'overall_score', 'completion_date'),
    )
    
    def __repr__(self) -> str:
        return (f"<Assessment(id={self.id}, "
                f"team_name='{self.team_name}', status='{self.status}')>")
    
    def validate(self) -> List[str]:
        """Validate assessment data"""
        errors = super().validate()
        
        if self.team_name and len(self.team_name) > 200:
            errors.append("Team name must be 200 characters or less")
        
        # Validate status
        valid_statuses = ['IN_PROGRESS', 'COMPLETED', 'DRAFT', 'LOCKED']
        if self.status not in valid_statuses:
            errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Validate score ranges
        if self.overall_score is not None and self.overall_score < 0:
            errors.append("Overall score must be non-negative")
        
        if self.foundational_score is not None and self.foundational_score < 0:
            errors.append("Foundational score must be non-negative")
        
        if self.transformation_score is not None and self.transformation_score < 0:
            errors.append("Transformation score must be non-negative")
        
        if self.enterprise_score is not None and self.enterprise_score < 0:
            errors.append("Enterprise score must be non-negative")
        
        if self.governance_score is not None and self.governance_score < 0:
            errors.append("Governance score must be non-negative")
        
        if (self.assessment_duration_minutes is not None and 
            self.assessment_duration_minutes < 0):
            errors.append("Assessment duration must be non-negative")
        
        return errors
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get detailed assessment results
        
        Returns:
            Results dictionary
        """
        try:
            if self.results_json:
                return json.loads(self.results_json)
            return {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_results(self, results: Dict[str, Any]) -> None:
        """
        Set detailed assessment results
        
        Args:
            results: Results dictionary
        """
        self.results_json = json.dumps(results)
    
    def start_assessment(self) -> None:
        """Mark assessment as started"""
        if self.status == 'DRAFT':
            self.status = 'IN_PROGRESS'
    
    def complete_assessment(self) -> None:
        """Mark assessment as completed"""
        if self.status == 'IN_PROGRESS':
            self.status = 'COMPLETED'
            self.completion_date = datetime.utcnow()

    def lock(self) -> None:
        """Lock assessment to prevent modification (post-completion)."""
        if self.status == 'COMPLETED':
            self.status = 'LOCKED'
    
    @property
    def is_draft(self) -> bool:
        """Check if assessment is in draft status"""
        return self.status == 'DRAFT'
    
    @property
    def is_in_progress(self) -> bool:
        """Check if assessment is in progress"""
        return self.status == 'IN_PROGRESS'
    
    @property
    def is_completed(self) -> bool:
        """Check if assessment is completed"""
        return self.status == 'COMPLETED'

    @property
    def is_locked(self) -> bool:
        """Check if assessment is locked (immutable)."""
        return self.status == 'LOCKED'
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert to dictionary with parsed JSON fields"""
        result = super().to_dict(include_relationships)
        
        # Parse JSON fields for easier consumption
        result['results'] = self.get_results()
        
        return result


__all__ = ['Assessment', 'AssessmentStatus']
