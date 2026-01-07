"""
Area Domain Detail Provider

Provides risk context and references for each area. Loads from JSON if available,
falls back to built-in defaults. Used by report rendering.
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


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


def _load_json_details() -> Dict[str, Dict]:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # Try data/area_domain_details.json at repo root
    candidate = os.path.join(base_dir, 'data', 'area_domain_details.json')
    if os.path.exists(candidate):
        try:
            with open(candidate, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


_JSON_DETAILS = _load_json_details()


def get_area_domain_detail(area_id: str) -> Optional[AreaDomainDetail]:
    """
    Return AreaDomainDetail for a given area_id using JSON overrides
    if present, else built-in defaults.
    """
    src = _JSON_DETAILS.get(area_id) or _DEFAULTS.get(area_id)
    if not src:
        return None
    return AreaDomainDetail(
        area_id=area_id,
        risk_description=src.get('risk_description'),
        references=src.get('references') or {}
    )
