"""
Lightweight i18n (internationalisation) support for AFS Assessment Framework.

Uses JSON translation files stored alongside this module.
Language preference is persisted in ``session['lang']`` and exposed to
every Jinja2 template via the ``_()`` helper and ``current_lang`` variable.
"""

import json
import os
from functools import lru_cache
from typing import Dict, Optional

from flask import session, request

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'pt': 'Português',
}
DEFAULT_LANGUAGE = 'en'

_TRANSLATIONS_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Translation loading
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _load_translations(lang: str) -> Dict[str, str]:
    """Load and cache the flat translation dict for *lang*."""
    path = os.path.join(_TRANSLATIONS_DIR, f'{lang}.json')
    if not os.path.isfile(path):
        return {}
    with open(path, 'r', encoding='utf-8') as fh:
        data: dict = json.load(fh)
    # Flatten nested dicts: {"nav": {"home": "Home"}} → {"nav.home": "Home"}
    flat: Dict[str, str] = {}
    _flatten(data, '', flat)
    return flat


def _flatten(obj: dict, prefix: str, out: Dict[str, str]) -> None:
    for key, value in obj.items():
        full_key = f'{prefix}{key}' if not prefix else f'{prefix}.{key}'
        if isinstance(value, dict):
            _flatten(value, full_key, out)
        else:
            out[full_key] = str(value)


def reload_translations() -> None:
    """Clear the translation cache (useful after editing JSON files)."""
    _load_translations.cache_clear()


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_locale() -> str:
    """Return the current language code from the session, falling back to
    the browser's ``Accept-Language`` header or the default."""
    lang = session.get('lang')
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang
    # Try browser preference
    if request:
        best = request.accept_languages.best_match(SUPPORTED_LANGUAGES.keys())
        if best:
            return best
    return DEFAULT_LANGUAGE


def translate(key: str, **kwargs) -> str:
    """Look up *key* in the current locale's translations.

    Supports ``{variable}`` interpolation via *kwargs*.
    Falls back to the English translation, then to the key itself so that
    missing translations are immediately visible during development.
    """
    lang = get_locale()
    translations = _load_translations(lang)
    text = translations.get(key)
    if text is None and lang != 'en':
        # Fallback to English
        text = _load_translations('en').get(key)
    if text is None:
        # Return the key as-is so missing translations are obvious
        return key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


# Convenient alias used in templates: {{ _('key') }}
_ = translate


def init_app(app):
    """Register the i18n context processor and language-switch route."""

    @app.context_processor
    def inject_i18n():
        return {
            '_': translate,
            'current_lang': get_locale(),
            'supported_languages': SUPPORTED_LANGUAGES,
        }

    @app.route('/set-language/<lang>')
    def set_language(lang):
        """Switch the UI language and redirect back."""
        from flask import redirect
        if lang in SUPPORTED_LANGUAGES:
            session['lang'] = lang
        referrer = request.referrer or '/'
        return redirect(referrer)
