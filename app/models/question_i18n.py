"""
Question Translation Provider

Loads bilingual question text and level descriptions from
``data/questions_i18n.json``.  The database stores the Portuguese
originals; this module overlays English (or any supported language)
at render time so the UI can switch seamlessly.

Usage::

    from app.models.question_i18n import get_question_text, get_level_desc

    text = get_question_text('ETSI-ESI-01A')          # uses current lang
    text = get_question_text('ETSI-ESI-01A', 'en')    # explicit English
    yes  = get_level_desc('level_2')                    # "Yes" / "Sim"
"""

import json
import os
from typing import Dict, Optional

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_I18N_FILE = os.path.join(_BASE_DIR, 'data', 'questions_i18n.json')

# Cache
_QUESTIONS_CACHE: Dict = {}
_LEVEL_DESCS_CACHE: Dict = {}
_FILE_MTIME: float = -1.0


def _get_current_lang() -> str:
    """Get the current language from the i18n module, defaulting to 'en'."""
    try:
        from app.i18n import get_locale
        return get_locale()
    except Exception:
        return 'en'


def _ensure_loaded() -> None:
    """Load (or reload) the questions i18n file when it changes."""
    global _QUESTIONS_CACHE, _LEVEL_DESCS_CACHE, _FILE_MTIME

    try:
        current_mtime = os.path.getmtime(_I18N_FILE) if os.path.exists(_I18N_FILE) else -1.0
    except Exception:
        current_mtime = -1.0

    reload_flag = os.environ.get('QUESTIONS_I18N_RELOAD', 'false').lower() == 'true'

    if _QUESTIONS_CACHE and not reload_flag and current_mtime == _FILE_MTIME:
        return

    if os.path.exists(_I18N_FILE):
        try:
            with open(_I18N_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            _QUESTIONS_CACHE = data.get('questions', {})
            _LEVEL_DESCS_CACHE = data.get('level_descriptions', {})
        except Exception:
            _QUESTIONS_CACHE = {}
            _LEVEL_DESCS_CACHE = {}

    _FILE_MTIME = current_mtime


def get_question_text(question_id: str, lang: Optional[str] = None) -> Optional[str]:
    """Return the translated question text for *question_id*.

    Returns ``None`` if no translation is available (caller should
    fall back to the database value).
    """
    _ensure_loaded()
    lang = lang or _get_current_lang()
    entry = _QUESTIONS_CACHE.get(question_id)
    if not entry:
        return None
    return entry.get(lang) or entry.get('en') or entry.get('pt')


def get_level_desc(level_key: str, lang: Optional[str] = None) -> Optional[str]:
    """Return the translated binary level description.

    *level_key* should be ``'level_1'`` or ``'level_2'`` (for binary
    Yes/No questions).  Returns ``None`` if not found.
    """
    _ensure_loaded()
    lang = lang or _get_current_lang()
    binary = _LEVEL_DESCS_CACHE.get('binary', {})
    lang_descs = binary.get(lang) or binary.get('en') or {}
    return lang_descs.get(level_key)


def get_all_translations(lang: Optional[str] = None) -> Dict[str, str]:
    """Return a dict mapping question_id → translated text for *lang*.

    Useful for bulk overlay in templates.
    """
    _ensure_loaded()
    lang = lang or _get_current_lang()
    result: Dict[str, str] = {}
    for qid, entry in _QUESTIONS_CACHE.items():
        text = entry.get(lang) or entry.get('en') or entry.get('pt')
        if text:
            result[qid] = text
    return result


def get_binary_labels(lang: Optional[str] = None) -> Dict[str, str]:
    """Return {'level_1': 'No'/'Não', 'level_2': 'Yes'/'Sim'} for *lang*."""
    _ensure_loaded()
    lang = lang or _get_current_lang()
    binary = _LEVEL_DESCS_CACHE.get('binary', {})
    return binary.get(lang) or binary.get('en') or {'level_1': 'No', 'level_2': 'Yes'}


def invalidate_question_i18n_cache() -> None:
    """Force question translations to reload on next access."""
    global _QUESTIONS_CACHE, _LEVEL_DESCS_CACHE, _FILE_MTIME
    _QUESTIONS_CACHE = {}
    _LEVEL_DESCS_CACHE = {}
    _FILE_MTIME = -1.0


__all__ = [
    'get_question_text',
    'get_level_desc',
    'get_all_translations',
    'get_binary_labels',
    'invalidate_question_i18n_cache',
]
