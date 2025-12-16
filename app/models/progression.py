"""
Maturity Progression Model for AFS Assessment Framework

This module defines the MaturityProgression model for accessing
step-by-step progression guidance for different maturity levels.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from .base import BaseModel


class MaturityProgression(BaseModel):
    """
    Maturity progression model
    
    Represents step-by-step guidance for achieving different maturity levels
    """
    
    __tablename__ = 'maturity_progressions'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to areas
    area_id = Column(String, ForeignKey('areas.id'), nullable=False)
    
    # Optional current level (1-3), and required target level (2-4)
    # Note: current_level is nullable for backward compatibility
    current_level = Column(Integer, nullable=True)
    # Target level (2, 3, or 4 - level 1 is baseline)
    target_level = Column(Integer, nullable=False)
    
    # Progression details
    prerequisites = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    success_metrics = Column(Text, nullable=True)
    timeline = Column(Text, nullable=True)
    common_pitfall = Column(Text, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'target_level >= 2 AND target_level <= 4',
            name='check_target_level'
        ),
        CheckConstraint(
            'current_level IS NULL OR (current_level >= 1 AND current_level <= 3)',
            name='check_current_level'
        ),
        {'sqlite_autoincrement': True}
    )
    
    # Relationships
    area = relationship('Area', backref='progressions')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert MaturityProgression to dictionary for JSON serialization
        
        Returns:
            Dictionary representation of the progression
        """
        return {
            'id': self.id,
            'area_id': self.area_id,
            'current_level': self.current_level,
            'target_level': self.target_level,
            'prerequisites': self.prerequisites,
            'action_items': self.action_items,
            'success_metrics': self.success_metrics,
            'timeline': self.timeline,
            'common_pitfall': self.common_pitfall
        }

    def __repr__(self) -> str:
        return (f"<MaturityProgression("
                f"area_id={self.area_id}, "
                f"target_level={self.target_level})>")
    
    def get_formatted_data(self) -> Dict[str, Any]:
        """Get progression data formatted for UI display"""
        return {
            'area_id': self.area_id,
            'target_level': self.target_level,
            'prerequisites': self._format_list_items(self.prerequisites),
            'action_items': self._format_action_items(self.action_items),
            'success_metrics': self._format_list_items(self.success_metrics),
            'timeline': self.timeline,
            'common_pitfall': self.common_pitfall
        }
    
    def _format_list_items(self, text: str) -> List[str]:
        """Format pipe-separated list items"""
        if not text:
            return []
        return [item.strip() for item in text.split('|') if item.strip()]
    
    def _format_action_items(self, text: str) -> List[Dict[str, Any]]:
        """Format action items into categories with sub-items"""
        if not text:
            return []
        
        action_items = []
        sections = text.split('|')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            if ':' in section:
                # This is a category with sub-items
                parts = section.split(':', 1)
                category = parts[0].strip()
                items_text = parts[1].strip()
                
                # Split sub-items by comma
                sub_items = [
                    item.strip()
                    for item in items_text.split(',')
                    if item.strip()
                ]
                
                action_items.append({
                    'category': category,
                    'items': sub_items
                })
            else:
                # This is a standalone item
                action_items.append({
                    'category': None,
                    'items': [section]
                })
        
        return action_items


def get_progression_for_area_level(
    area_id: str, level: int
) -> Optional[MaturityProgression]:
    """
    Get progression data for a specific area and level
    
    Args:
        area_id: The area ID
        level: The target level (2, 3, or 4)
    
    Returns:
        MaturityProgression object or None if not found
    """
    from app.extensions import db
    
    return db.session.query(MaturityProgression).filter(
        MaturityProgression.area_id == area_id,
        MaturityProgression.target_level == level
    ).first()


def get_all_progressions_for_area(
    area_id: str
) -> Dict[int, MaturityProgression]:
    """
    Get all progression data for a specific area
    
    Args:
        area_id: The area ID
    
    Returns:
        Dictionary mapping level to MaturityProgression object
    """
    from app.extensions import db
    
    progressions = db.session.query(MaturityProgression).filter(
        MaturityProgression.area_id == area_id
    ).all()
    
    return {prog.target_level: prog for prog in progressions}


def get_recommendations_for_area_current_level(
    area_id: str, current_level: int
) -> Optional[MaturityProgression]:
    """
    Get the recommended progression entry for the next maturity level, based on
    the area's current maturity level.

    Selection rules:
    - Prefer entries where current_level matches and target_level == current_level + 1
    - Fallback to generic entries where current_level is NULL with target_level == current_level + 1
    - Return None if current_level >= 4 or no suitable progression exists
    """
    if current_level >= 4:
        return None
    from app.extensions import db
    # Prefer specific from->to mapping
    progression = db.session.query(MaturityProgression).filter(
        MaturityProgression.area_id == area_id,
        MaturityProgression.current_level == current_level,
        MaturityProgression.target_level == current_level + 1
    ).first()
    if progression:
        return progression
    # Fallback to generic target-level-only entry
    progression = db.session.query(MaturityProgression).filter(
        MaturityProgression.area_id == area_id,
        MaturityProgression.current_level.is_(None),
        MaturityProgression.target_level == current_level + 1
    ).first()
    return progression


__all__ = [
    'MaturityProgression',
    'get_progression_for_area_level',
    'get_all_progressions_for_area',
    'get_recommendations_for_area_current_level'
]
