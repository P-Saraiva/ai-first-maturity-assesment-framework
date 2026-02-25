"""
Area Domain Detail Provider

Provides risk context and references for each area. Loads from JSON if available,
falls back to built-in defaults. Used by report rendering.

Supports bilingual (en/pt) content. The JSON files can store values as either:
  - A plain string (legacy format, treated as Portuguese)
  - A dict with 'en' and 'pt' keys (bilingual format)

The current language is resolved via the i18n module's get_locale().
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_DETAILS_FILE = os.path.join(_BASE_DIR, 'data', 'area_domain_details.json')
_MATURITY_FILE = os.path.join(_BASE_DIR, 'data', 'area_maturity_definitions.json')


def _resolve_lang_value(value, lang: str):
    """Resolve a value that may be bilingual (dict with 'en'/'pt') or plain.

    If *value* is a dict with language keys, return the value for *lang*,
    falling back to 'en', then 'pt', then the first available value.
    Otherwise return the value as-is (legacy plain string/list).
    """
    if isinstance(value, dict) and ('en' in value or 'pt' in value):
        return value.get(lang) or value.get('en') or value.get('pt') or ''
    return value


def _get_current_lang() -> str:
    """Get the current language from the i18n module, defaulting to 'en'."""
    try:
        from app.i18n import get_locale
        return get_locale()
    except Exception:
        return 'en'


@dataclass
class AreaDomainDetail:
    area_id: str
    risk_description: Optional[str]
    references: Dict[str, List[str]]

    def to_dict(self) -> Dict:
        return {
            'risk_description': self.risk_description or '',
            'references': {
                'mitre': self.references.get('mitre', []),
                'nist': self.references.get('nist', [])
            }
        }


_DEFAULTS: Dict[str, Dict] = {
    # ETSI
    'ETSI-ESI': {
        'risk_description': 'Uso inadequado de IA pode impactar direitos, causar vieses e afetar stakeholders sem transparência adequada.',
        'references': {
            'mitre': ['ATLAS: Ethical considerations and bias'],
            'nist': ['AI RMF: Govern, Map, Measure, Manage — Transparency and Accountability']
        }
    },
    'ETSI-ETC': {
        'risk_description': 'Falta de explicabilidade pode reduzir confiança e dificultar auditoria de decisões automatizadas.',
        'references': {
            'mitre': ['ATLAS: Model explainability challenges'],
            'nist': ['AI RMF: Transparency, Documentation and Communication']
        }
    },
    'ETSI-BFR': {
        'risk_description': 'Dados e modelos podem introduzir vieses, causando impactos discriminatórios em processos decisórios.',
        'references': {
            'mitre': ['ATLAS: Data poisoning and bias'],
            'nist': ['AI RMF: Harm mitigation, Fairness']
        }
    },
    # GSA
    'GSA-GSC': {
        'risk_description': 'Ausência de governança e métricas pode levar a decisões incoerentes e riscos regulatórios.',
        'references': {
            'mitre': ['ATLAS: Governance and compliance patterns'],
            'nist': ['AI RMF: Governance functions and roles']
        }
    },
    'GSA-PLA': {
        'risk_description': 'Não conformidade com LGPD/GDPR e requisitos éticos pode resultar em sanções e prejuízos reputacionais.',
        'references': {
            'mitre': ['ATLAS: Legal and regulatory considerations'],
            'nist': ['AI RMF: Risk management, Documentation']
        }
    },
    'GSA-CUL': {
        'risk_description': 'Cultura fraca de segurança em IA aumenta probabilidade de erros operacionais e exposição a ameaças.',
        'references': {
            'mitre': ['ATLAS: Organizational readiness'],
            'nist': ['AI RMF: Training and awareness']
        }
    },
    # IAA
    'IAA-IGO': {
        'risk_description': 'Identidades de agentes e sistemas de IA sem governança clara podem permitir ações não rastreáveis.',
        'references': {
            'mitre': ['ATLAS: Identity and access risks for AI systems'],
            'nist': ['AI RMF: Access control and accountability']
        }
    },
    'IAA-CSM': {
        'risk_description': 'Gestão inadequada de segredos e credenciais de IA pode permitir abuso e comprometimento de sistemas.',
        'references': {
            'mitre': ['ATLAS: Credential abuse and secret leakage'],
            'nist': ['AI RMF: Secure development and operations']
        }
    },
    'IAA-AAP': {
        'risk_description': 'Agentes com privilégio elevado sem supervisão humana podem executar ações perigosas ou irreversíveis.',
        'references': {
            'mitre': ['ATLAS: Autonomous agent risks'],
            'nist': ['AI RMF: Human oversight (“human-in-the-loop”)']
        }
    },
    # DPR
    'DPR-IPU': {
        'risk_description': 'Inventário incompleto e falta de proveniência facilitam “Shadow AI” e uso de componentes vulneráveis.',
        'references': {
            'mitre': ['ATLAS: Supply chain and third-party risks'],
            'nist': ['AI RMF: Asset management and provenance']
        }
    },
    'DPR-DGM': {
        'risk_description': 'Dados de baixa qualidade e governança fraca comprometem resultados e segurança dos sistemas de IA.',
        'references': {
            'mitre': ['ATLAS: Data integrity and governance'],
            'nist': ['AI RMF: Data quality and integrity']
        }
    },
    # PUT
    'PUT-PUC': {
        'risk_description': 'Falta de transparência e controle para usuários pode violar privacidade e reduzir confiança.',
        'references': {
            'mitre': ['ATLAS: Privacy risks and transparency'],
            'nist': ['AI RMF: Privacy-by-design, User control']
        }
    },
    # TSA
    'TSA-TRO': {
        'risk_description': 'Ameaças específicas de IA (prompt injection, model abuse) exigem mitigação contínua.',
        'references': {
            'mitre': ['ATLAS: Prompt injection, Model abuse'],
            'nist': ['AI RMF: Threat modeling and risk mitigation']
        }
    },
    'TSA-SDA': {
        'risk_description': 'Implantação sem critérios e arquitetura segura pode expor modelos e dados sensíveis.',
        'references': {
            'mitre': ['ATLAS: Secure deployment patterns'],
            'nist': ['AI RMF: Secure operations and release management']
        }
    },
    'TSA-DMH': {
        'risk_description': 'Falhas não rastreadas e ausência de bloqueio de conteúdo nocivo ampliam impactos negativos.',
        'references': {
            'mitre': ['ATLAS: Defect management, Content safety'],
            'nist': ['AI RMF: Monitoring and incident response']
        }
    },
    # QEI
    'QEI-TEI': {
        'risk_description': 'Ausência de testes adequados permite que riscos passem despercebidos para produção.',
        'references': {
            'mitre': ['ATLAS: Testing and evaluation'],
            'nist': ['AI RMF: Measurement and evaluation']
        }
    },
    'QEI-IEC': {
        'risk_description': 'Falta de resposta a incidentes específicos de IA aumenta tempo de impacto e danos.',
        'references': {
            'mitre': ['ATLAS: Incident response for AI'],
            'nist': ['AI RMF: Incident management and recovery']
        }
    },
    'QEI-OCM': {
        'risk_description': 'Operação sem monitoramento contínuo impede detectar desvios e riscos em tempo hábil.',
        'references': {
            'mitre': ['ATLAS: Continuous monitoring'],
            'nist': ['AI RMF: Continuous improvement']
        }
    },
}


def _compute_latest_mtime() -> float:
    try:
        m1 = os.path.getmtime(_DETAILS_FILE) if os.path.exists(_DETAILS_FILE) else -1.0
    except Exception:
        m1 = -1.0
    try:
        m2 = os.path.getmtime(_MATURITY_FILE) if os.path.exists(_MATURITY_FILE) else -1.0
    except Exception:
        m2 = -1.0
    return max(m1, m2)


def _load_json_details() -> Dict[str, Dict]:
    """Load raw JSON data (preserving bilingual dicts as-is).

    Language resolution happens later in get_area_domain_detail().
    """
    result: Dict[str, Dict] = {}
    if os.path.exists(_DETAILS_FILE):
        try:
            with open(_DETAILS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    result.update(data)
        except Exception:
            pass

    # Also merge risk/references from area_maturity_definitions.json if present
    if os.path.exists(_MATURITY_FILE):
        try:
            with open(_MATURITY_FILE, 'r', encoding='utf-8') as f:
                data2 = json.load(f)
                if isinstance(data2, dict):
                    for area_id, payload in data2.items():
                        if not isinstance(payload, dict):
                            continue
                        rd = payload.get('risk_description')
                        refs = payload.get('references')
                        if rd or refs:
                            merged = result.get(area_id, {}).copy()
                            if rd:
                                merged['risk_description'] = rd
                            if isinstance(refs, dict):
                                existing_refs = merged.get('references') or {}
                                new_refs = {
                                    'mitre': refs.get('mitre', existing_refs.get('mitre', [])),
                                    'nist': refs.get('nist', existing_refs.get('nist', [])),
                                }
                                merged['references'] = new_refs
                            result[area_id] = merged
        except Exception:
            pass

    return result


_JSON_DETAILS: Dict[str, Dict] = {}
_JSON_MTIME: float = -1.0


def _ensure_loaded() -> None:
    global _JSON_DETAILS, _JSON_MTIME
    reload_flag = os.environ.get('AREA_DOMAIN_RELOAD', 'false').lower() == 'true'
    latest = _compute_latest_mtime()
    if _JSON_DETAILS and not reload_flag and latest == _JSON_MTIME:
        return
    _JSON_DETAILS = _load_json_details()
    _JSON_MTIME = latest


def get_area_domain_detail(area_id: str) -> Optional[AreaDomainDetail]:
    """
    Return AreaDomainDetail for a given area_id using JSON overrides
    if present, else built-in defaults.

    Bilingual fields are resolved to the current session language
    via the i18n module's get_locale().
    """
    _ensure_loaded()
    src = _JSON_DETAILS.get(area_id) or _DEFAULTS.get(area_id)
    if not src:
        return None

    lang = _get_current_lang()

    # Resolve risk_description (may be a bilingual dict or plain string)
    raw_rd = src.get('risk_description')
    risk_description = _resolve_lang_value(raw_rd, lang) if raw_rd else None

    # Resolve references (each sub-key may be bilingual)
    raw_refs = src.get('references') or {}
    resolved_refs: Dict[str, List[str]] = {}
    for ref_key in ('mitre', 'nist'):
        raw_val = raw_refs.get(ref_key, [])
        resolved = _resolve_lang_value(raw_val, lang)
        if isinstance(resolved, list):
            resolved_refs[ref_key] = resolved
        elif isinstance(resolved, str):
            resolved_refs[ref_key] = [resolved]
        else:
            resolved_refs[ref_key] = []

    return AreaDomainDetail(
        area_id=area_id,
        risk_description=risk_description,
        references=resolved_refs
    )

def invalidate_area_domain_cache() -> None:
    """Force area domain details to reload on next access."""
    global _JSON_DETAILS, _JSON_MTIME
    _JSON_DETAILS = {}
    _JSON_MTIME = -1.0
