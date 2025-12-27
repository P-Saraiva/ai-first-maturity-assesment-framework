"""
Maturity Definition Model for AFS Assessment Framework

Provides definitions/descriptions for the CURRENT maturity level of
an entity (area or question). This is distinct from the legacy
maturity_progressions table which focuses on next-level roadmaps.
"""
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import validates
from .base import BaseModel


class MaturityDefinition(BaseModel):
    __tablename__ = 'maturity_definitions'

    entity_type = Column(String, nullable=False)  # 'area' | 'question'
    entity_id = Column(String, nullable=False)
    maturity_level = Column(Integer, nullable=False)

    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    characteristics = Column(Text, nullable=True)
    expectations = Column(Text, nullable=True)
    guidance = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("entity_type in ('area','question')", name='check_entity_type'),
        CheckConstraint('maturity_level >= 1 AND maturity_level <= 5', name='check_maturity_level'),
        {
            'sqlite_autoincrement': True
        }
    )

    @validates('entity_type')
    def validate_entity_type(self, key, value):
        if value not in ('area', 'question'):
            raise ValueError('entity_type must be area or question')
        return value

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'maturity_level': self.maturity_level,
            'title': self.title,
            'summary': self.summary,
            'characteristics': self.characteristics,
            'expectations': self.expectations,
            'guidance': self.guidance
        }


def get_area_definition(area_id: str, level: int) -> Optional[MaturityDefinition]:
    from app.extensions import db
    try:
        return db.session.query(MaturityDefinition).filter(
            MaturityDefinition.entity_type == 'area',
            MaturityDefinition.entity_id == area_id,
            MaturityDefinition.maturity_level == level
        ).first()
    except Exception:
        # Table may not exist yet; fail gracefully
        return None


def get_area_definitions(area_id: str) -> Dict[int, MaturityDefinition]:
    from app.extensions import db
    try:
        rows = db.session.query(MaturityDefinition).filter(
            MaturityDefinition.entity_type == 'area',
            MaturityDefinition.entity_id == area_id
        ).all()
        return {row.maturity_level: row for row in rows}
    except Exception:
        return {}


__all__ = [
    'MaturityDefinition',
    'get_area_definition',
    'get_area_definitions',
]
