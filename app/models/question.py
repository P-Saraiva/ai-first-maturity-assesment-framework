"""
Question Model for AFS Assessment Framework

This module defines the Question model and related entities for
the assessment framework.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Boolean, 
    CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, validates

from .base import BaseModel


class Section(BaseModel):
    """
    Assessment section model
    
    Represents major sections of the assessment framework
    """
    
    __tablename__ = 'sections'
    
    # Override the id to match database schema (TEXT instead of Integer)
    id = Column(String, primary_key=True)
    
    # Basic fields - matching actual database schema
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    color = Column(Text, default='#3b82f6', nullable=True)
    icon = Column(Text, default='fas fa-cog', nullable=True)
    
    # Relationships
    areas = relationship(
        'Area', 
        back_populates='section',
        cascade='all, delete-orphan',
        order_by='Area.display_order'
    )

    def __repr__(self) -> str:
        return f"<Section(id={self.id}, name='{self.name}')>"


class Area(BaseModel):
    """
    Assessment area model
    
    Represents assessment areas within sections
    """
    
    __tablename__ = 'areas'
    
    # Override the id to match database schema (TEXT instead of Integer)
    id = Column(String, primary_key=True)
    
    # Basic fields - matching actual database schema
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    
    # Timeline fields specific to this schema
    timeline_l1_l2 = Column(Text, nullable=True)
    timeline_l2_l3 = Column(Text, nullable=True)
    timeline_l3_l4 = Column(Text, nullable=True)
    
    # Foreign keys - matching database schema (TEXT not Integer)
    section_id = Column(String, ForeignKey('sections.id'), nullable=False)
    
    # Relationships
    section = relationship('Section', back_populates='areas')
    questions = relationship(
        'Question',
        back_populates='area',
        cascade='all, delete-orphan',
        order_by='Question.display_order'
    )

    def __repr__(self) -> str:
        return f"<Area(id={self.id}, name='{self.name}')>"


class Question(BaseModel):
    """
    Assessment question model
    
    Represents individual questions within areas
    """
    
    __tablename__ = 'questions'
    
    # Override the id to match database schema (TEXT instead of Integer)
    id = Column(String, primary_key=True)
    
    # Basic fields - matching actual database schema
    question = Column(Text, nullable=False)  # This is 'question' not 'text'
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Integer, default=1, nullable=False)  # INTEGER not String
    
    # Level descriptions instead of answer_options
    level_1_desc = Column(Text, nullable=True)
    level_2_desc = Column(Text, nullable=True)
    level_3_desc = Column(Text, nullable=True)
    level_4_desc = Column(Text, nullable=True)
    
    # Foreign keys - matching database schema (TEXT not Integer)
    area_id = Column(String, ForeignKey('areas.id'), nullable=False)
    
    # Relationships
    area = relationship('Area', back_populates='questions')
    responses = relationship(
        'Response',
        back_populates='question',
        cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, question='{self.question[:50]}...')>"
    
    def get_level_descriptions(self) -> List[Dict[str, Any]]:
        """Get level descriptions as a list of dictionaries"""
        levels = []
        for i in range(1, 5):
            level_desc = getattr(self, f'level_{i}_desc', None)
            if level_desc:
                levels.append({
                    'level': i,
                    'description': level_desc,
                    'score': i
                })
        return levels

    @property
    def is_binary(self) -> bool:
        """Infer if this question is binary Yes/No based on ID suffix.

        Binary checklist items follow an ID convention like FC-AIT-01A .. FC-AIT-01F.
        We treat these as binary items that will be grouped into a single logical question
        for scoring and coverage purposes.
        """
        try:
            if not isinstance(self.id, str):
                return False
            if len(self.id) < 2:
                return False
            suffix = self.id[-1]
            if suffix in 'ABCDEF':
                base = self.id[:-1]
                return base[-2:].isdigit()
            # Also consider two-level binary where only 1/2 levels used
            # by checking presence of level_3_desc and level_4_desc as empty while 1/2 exist
            has_l1 = bool(self.level_1_desc)
            has_l2 = bool(self.level_2_desc)
            has_l3 = bool(self.level_3_desc)
            has_l4 = bool(self.level_4_desc)
            return has_l1 and has_l2 and not has_l3 and not has_l4
        except Exception:
            return False

    @property
    def binary_weight(self) -> float:
        """Derived binary weight for this question.

        As the schema does not persist weights, default to 1.0 for all
        binary questions for a fair weighted average, and 0.0 for non-binary
        questions so they are naturally ignored by binary scoring.
        """
        try:
            return 1.0 if self.is_binary else 0.0
        except Exception:
            return 0.0

    @property
    def binary_level(self) -> int:
        """Derived maturity level (1..4) for this binary question.

        We infer from the A-F suffix position within a six-item checklist:
        - A,B -> Level 1
        - C   -> Level 2
        - D,E -> Level 3
        - F   -> Level 4
        For items without A-F suffix, default to Level 1.
        """
        try:
            if not isinstance(self.id, str) or len(self.id) == 0:
                return 1
            suffix = self.id[-1]
            mapping = {
                'A': 1,
                'B': 1,
                'C': 2,
                'D': 3,
                'E': 3,
                'F': 4,
            }
            return mapping.get(suffix, 1)
        except Exception:
            return 1


__all__ = ['Section', 'Area', 'Question']
