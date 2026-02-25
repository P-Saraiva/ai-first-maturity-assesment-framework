"""
Scoring utility functions for AFS Assessment Framework

Simple percentage-based scoring for binary (Yes/No) questions.
Each question is scored 1 (No) or 2 (Yes).  A "Yes" counts as a
confirmed capability.  The percentage of "Yes" answers drives all
classification.

SSE-CMM-inspired 5-level maturity classification:
    0–20 %  → Informal
   21–40 %  → Defined
   41–60 %  → Systematic
   61–80 %  → Integrated
   81–100 % → Optimized
"""

from typing import Dict, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SSE-CMM 5-level maturity
# ---------------------------------------------------------------------------

class SSELevel(Enum):
    """SSE-CMM-inspired 5-level maturity classification."""
    INFORMAL = "Informal"
    DEFINED = "Defined"
    SYSTEMATIC = "Systematic"
    INTEGRATED = "Integrated"
    OPTIMIZED = "Optimized"


class SSEConstants:
    """Thresholds and helpers for SSE-CMM percentage-based scoring."""

    # (level, lower_bound_inclusive, upper_bound_inclusive)
    LEVEL_THRESHOLDS = [
        (SSELevel.INFORMAL,    0.00, 0.20),
        (SSELevel.DEFINED,     0.21, 0.40),
        (SSELevel.SYSTEMATIC,  0.41, 0.60),
        (SSELevel.INTEGRATED,  0.61, 0.80),
        (SSELevel.OPTIMIZED,   0.81, 1.00),
    ]

    # Area weights – empty dict means equal weighting everywhere.
    AREA_WEIGHTS: Dict[str, float] = {}

    # Section weights – empty dict means equal weighting everywhere.
    SECTION_WEIGHTS: Dict[str, float] = {}

    @staticmethod
    def classify_percentage(p: float) -> SSELevel:
        """Map a 0‥1 percentage to the corresponding SSE level."""
        p = max(0.0, min(1.0, p))
        for level, lo, hi in SSEConstants.LEVEL_THRESHOLDS:
            if lo <= p <= hi:
                return level
        return SSELevel.INFORMAL

    @staticmethod
    def get_level_details(level: SSELevel) -> Dict:
        """Human-readable description for an SSE level."""
        details = {
            SSELevel.INFORMAL: {
                "name": "Informal",
                "description": (
                    "Ad-hoc controls; limited consistency; "
                    "practices not standardized."
                ),
            },
            SSELevel.DEFINED: {
                "name": "Defined",
                "description": (
                    "Controls defined; initial standardization; "
                    "repeatable in pockets."
                ),
            },
            SSELevel.SYSTEMATIC: {
                "name": "Systematic",
                "description": (
                    "Controls systematically applied; governance "
                    "emerging; wider coverage."
                ),
            },
            SSELevel.INTEGRATED: {
                "name": "Integrated",
                "description": (
                    "Controls integrated across lifecycle; "
                    "cross-functional adoption; measurable."
                ),
            },
            SSELevel.OPTIMIZED: {
                "name": "Optimized",
                "description": (
                    "Controls optimized; continuous improvement; "
                    "predictive and proactive."
                ),
            },
        }
        return details.get(level, {"name": level.value, "description": ""})

    @staticmethod
    def level_to_number(level: SSELevel) -> int:
        """Convert SSE level to 1-5 numeric rank."""
        mapping = {
            SSELevel.INFORMAL: 1,
            SSELevel.DEFINED: 2,
            SSELevel.SYSTEMATIC: 3,
            SSELevel.INTEGRATED: 4,
            SSELevel.OPTIMIZED: 5,
        }
        return mapping.get(level, 1)


# ---------------------------------------------------------------------------
# Backward-compatible constants (kept for any remaining callers)
# ---------------------------------------------------------------------------

class ScoringConstants:
    """Minimal constants kept for backward compatibility."""
    MIN_SCORE = 1.0
    MAX_SCORE = 4.0


# Alias so old `from scoring_utils import LegacyMaturityLevel` still works
LegacyMaturityLevel = SSELevel


# ---------------------------------------------------------------------------
# Core math helpers
# ---------------------------------------------------------------------------

def simple_average(values: List[float]) -> float:
    """Return the arithmetic mean of *values*, or 0.0 if empty."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_weighted_average(scores: List[float],
                               weights: List[float] = None) -> float:
    """Weighted average; falls back to simple average when weights is None."""
    if not scores:
        return 0.0
    if weights is None:
        return simple_average(scores)
    if len(scores) != len(weights):
        raise ValueError("Scores and weights must have the same length")
    total_w = sum(weights)
    if total_w == 0:
        return simple_average(scores)
    return sum(s * w for s, w in zip(scores, weights)) / total_w


def calculate_section_coverage(responded: int, total: int) -> float:
    """Fraction of questions answered (0‥1)."""
    if total <= 0:
        return 0.0
    return min(1.0, max(0.0, responded / total))


# ---------------------------------------------------------------------------
# Display / formatting helpers
# ---------------------------------------------------------------------------

def format_score_display(score: float, precision: int = 1) -> str:
    """Format a numeric score for display."""
    if not isinstance(score, (int, float)):
        return "N/A"
    return f"{score:.{precision}f}"


def validate_score_inputs(scores: List[float],
                          weights: List[float] = None) -> bool:
    """Light validation – kept for callers that still invoke it."""
    if not scores:
        raise ValueError("Scores list cannot be empty")
    return True


# ---------------------------------------------------------------------------
# Backward-compatible stubs (simplified)
# ---------------------------------------------------------------------------

def classify_maturity_level(score: float) -> Tuple:
    """Map a 1‥4 legacy score to an SSE level (backward compat)."""
    pct = max(0.0, min(1.0, (score - 1.0) / 3.0))
    level = SSEConstants.classify_percentage(pct)
    return level, level.value


def get_maturity_level_details(level) -> Dict:
    """Return details dict for any level enum."""
    if isinstance(level, SSELevel):
        return SSEConstants.get_level_details(level)
    return {}


def normalize_score(score: float, **_kwargs) -> float:
    """Passthrough – no longer transforms."""
    return float(score)


def calculate_improvement_potential(current_score: float,
                                   target_level=None) -> Dict:
    """Simplified improvement potential based on percentage."""
    pct = max(0.0, min(1.0, (current_score - 1.0) / 3.0))
    level = SSEConstants.classify_percentage(pct)
    return {
        'current_score': current_score,
        'current_level': level.value,
        'target_level': 'Optimized',
        'target_min_score': 4.0,
        'target_max_score': 4.0,
        'gap_to_target': round(max(0.0, 1.0 - pct) * 100, 1),
        'potential_improvement': round(max(0.0, 1.0 - pct) * 100, 1),
        'is_achievable': pct < 1.0,
    }
