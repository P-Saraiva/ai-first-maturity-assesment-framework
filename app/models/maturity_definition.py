"""
Maturity Definitions (Area and Question)

Provides configuration-driven maturity level definitions that describe the
current state characteristics, guidance, and expectations for each level.

This decouples "roadmap to next level" (MaturityProgression) from
"current level description" (MaturityDefinition).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

from app.utils.scoring_utils import SSELevel, SSEConstants


DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'data',
    'area_maturity_definitions.json'
)


_AREA_DEFS_CACHE: Dict[str, Dict[int, "MaturityDefinition"]] = {}
_AREA_DEFS_MTIME: float = -1.0


@dataclass
class MaturityDefinition:
    entity_type: str  # 'area' or 'question'
    entity_id: str
    maturity_level: int  # 1..5
    title: str
    description: str
    characteristics: Optional[str] = None  # pipe-delimited
    guidance: Optional[str] = None         # pipe-delimited
    expectations: Optional[str] = None     # pipe-delimited

    def to_dict(self) -> Dict:
        return {
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'maturity_level': self.maturity_level,
            'title': self.title,
            'description': self.description,
            'characteristics': self._split(self.characteristics),
            'guidance': self._split(self.guidance),
            'expectations': self._split(self.expectations),
        }

    @staticmethod
    def _split(text: Optional[str]) -> Optional[list]:
        if not text:
            return []
        return [t.strip() for t in text.split('|') if t.strip()]


def _load_area_defs() -> Dict[str, Dict[int, MaturityDefinition]]:
    """Load area definitions from JSON file, with sensible defaults."""
    global _AREA_DEFS_CACHE, _AREA_DEFS_MTIME

    # Support live-reload when file changes or when env flag is set
    reload_flag = os.environ.get('MATURITY_DEFS_RELOAD', 'false').lower() == 'true'
    current_mtime = None
    try:
        current_mtime = os.path.getmtime(DATA_FILE) if os.path.exists(DATA_FILE) else -1.0
    except Exception:
        current_mtime = -1.0

    if _AREA_DEFS_CACHE and not reload_flag:
        # If cached and file unchanged, return cache
        if current_mtime == _AREA_DEFS_MTIME:
            return _AREA_DEFS_CACHE

    defs: Dict[str, Dict[int, MaturityDefinition]] = {}

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            # Expected shape: { area_id: { level: { title, description, ... } } }
            for area_id, levels in raw.items():
                defs[area_id] = {}
                for level_str, payload in levels.items():
                    try:
                        level = int(level_str)
                    except Exception:
                        continue
                    defs[area_id][level] = MaturityDefinition(
                        entity_type='area',
                        entity_id=area_id,
                        maturity_level=level,
                        title=payload.get('title') or _default_title(level),
                        description=payload.get('description') or _default_description(level),
                        characteristics=_join(payload.get('characteristics')),
                        guidance=_join(payload.get('guidance')),
                        expectations=_join(payload.get('expectations')),
                    )
        except Exception:
            # Fall back to defaults if file is malformed
            pass

    # Provide default definitions for all areas/levels if none loaded
    if not defs:
        # Defaults: use SSEConstants level details
        # Since area list may be dynamic, we serve generic definitions keyed by '*'
        generic: Dict[int, MaturityDefinition] = {}
        for lvl_num, lvl_enum in enumerate([
            SSELevel.INFORMAL, SSELevel.DEFINED, SSELevel.SYSTEMATIC, SSELevel.INTEGRATED, SSELevel.OPTIMIZED
        ], start=1):
            details = SSEConstants.get_level_details(lvl_enum)
            generic[lvl_num] = MaturityDefinition(
                entity_type='area',
                entity_id='*',
                maturity_level=lvl_num,
                title=f"Level {lvl_num}: {details['name']}",
                description=details.get('description', ''),
                characteristics=None,
                guidance=None,
                expectations=None,
            )
        defs['*'] = generic

    _AREA_DEFS_CACHE = defs
    _AREA_DEFS_MTIME = current_mtime
    return defs


def _default_title(level: int) -> str:
    enum = [SSELevel.INFORMAL, SSELevel.DEFINED, SSELevel.SYSTEMATIC, SSELevel.INTEGRATED, SSELevel.OPTIMIZED][level-1]
    return f"Level {level}: {SSEConstants.get_level_details(enum)['name']}"


def _default_description(level: int) -> str:
    enum = [SSELevel.INFORMAL, SSELevel.DEFINED, SSELevel.SYSTEMATIC, SSELevel.INTEGRATED, SSELevel.OPTIMIZED][level-1]
    return SSEConstants.get_level_details(enum).get('description', '')


def _join(value) -> Optional[str]:
    if not value:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return '|'.join([str(v).strip() for v in value if str(v).strip()])
    return None


def get_area_definitions(area_id: str) -> Dict[int, MaturityDefinition]:
    """
    Return all maturity definitions for a given area, mapping 1..5.
    Falls back to generic definitions if area-specific not found.
    """
    defs = _load_area_defs()
    area_defs = defs.get(area_id) or defs.get('*') or {}
    # Ensure full 1..5 mapping
    for level in range(1, 6):
        if level not in area_defs:
            area_defs[level] = MaturityDefinition(
                entity_type='area',
                entity_id=area_id,
                maturity_level=level,
                title=_default_title(level),
                description=_default_description(level),
            )
    return area_defs


def get_area_definition(area_id: str, level: int) -> Optional[MaturityDefinition]:
    """Return single maturity definition for area at given level (1..5)."""
    level = max(1, min(5, int(level)))
    defs = get_area_definitions(area_id)
    return defs.get(level)

def invalidate_area_defs_cache() -> None:
    """Force maturity definitions to reload on next access."""
    global _AREA_DEFS_CACHE, _AREA_DEFS_MTIME
    _AREA_DEFS_CACHE = {}
    _AREA_DEFS_MTIME = -1.0


__all__ = [
    'MaturityDefinition',
    'get_area_definitions',
    'get_area_definition',
]
