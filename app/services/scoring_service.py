"""
Scoring Service for AFS Assessment Framework

Simple percentage-based scoring.  Every binary question is Yes (score 2)
or No (score 1).  The percentage of "Yes" answers is the single metric
at every level: area → section → overall.

All classification uses the SSE-CMM 5-level model defined in scoring_utils.
"""

from typing import Dict, List
from sqlalchemy.orm import Session, joinedload
import logging

from app.models.assessment import Assessment
from app.models.response import Response
from app.models.question import Question, Section, Area
from app.utils.scoring_utils import (
    SSEConstants, SSELevel,
    simple_average, calculate_section_coverage,
    format_score_display,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: resolve active section IDs from config / env / DB
# ---------------------------------------------------------------------------

def _get_active_section_ids(session: Session) -> List[str]:
    """Return the list of section IDs the application should consider."""
    import os
    ids = None
    try:
        from flask import current_app
        cfg = current_app.config.get('ACTIVE_SECTION_IDS') if current_app else None
        if isinstance(cfg, str) and cfg.strip():
            ids = [s.strip() for s in cfg.split(',') if s.strip()]
        elif isinstance(cfg, (list, tuple)) and cfg:
            ids = [str(s).strip() for s in cfg if str(s).strip()]
    except Exception:
        pass
    if ids is None:
        env = os.environ.get('ACTIVE_SECTION_IDS')
        if env:
            ids = [s.strip() for s in env.split(',') if s.strip()]
    if ids is None and session is not None:
        try:
            ids = [s.id for s in session.query(Section).order_by(Section.display_order).all()]
        except Exception:
            ids = []
    return ids or []


# ═══════════════════════════════════════════════════════════════════════════
# ScoringService
# ═══════════════════════════════════════════════════════════════════════════

class ScoringService:
    """Calculate assessment scores using simple averages of binary answers."""

    def __init__(self, session: Session):
        self.session = session

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def calculate_assessment_score(self, assessment_id: int) -> Dict:
        """
        Score an entire assessment.

        Returns a dict consumed by the report route and seed scripts.
        The *percentage* fields are 0‥1 (fraction of "Yes" answers).
        """
        assessment = self.session.query(Assessment).filter_by(id=assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        logger.info(f"Calculating score for assessment {assessment_id}")

        allowed_ids = self._compute_allowed_question_ids()
        section_scores = self._score_all_sections(assessment_id, allowed_ids)

        # Overall percentage = average of section percentages (equal weight
        # per section).  Each section's percentage is already the average of
        # its own area percentages, so this is a proper two-level mean that
        # treats every section equally regardless of how many areas it has.
        section_pcts: List[float] = [
            sec.get('section_percentage', 0.0)
            for sec in section_scores.values()
        ]

        overall_percentage = simple_average(section_pcts)
        overall_level = SSEConstants.classify_percentage(overall_percentage)
        overall_score_0to5 = round(overall_percentage * 5.0, 2)

        completion = self._completion_status(assessment_id, allowed_ids)

        results = {
            'assessment_id': assessment_id,
            'assessment_name': assessment.team_name or f"Assessment {assessment_id}",

            # Primary metrics
            'overall_percentage': round(overall_percentage, 3),
            'overall_score_0to5': overall_score_0to5,
            'maturity_level': overall_level.name,
            'maturity_level_display': overall_level.value,
            'maturity_details': SSEConstants.get_level_details(overall_level),

            # Backward-compatible keys (kept so templates don't break)
            'deviq_score': round(1.0 + overall_percentage * 3.0, 2),
            'deviq_score_display': format_score_display(1.0 + overall_percentage * 3.0),
            'overall_normalized': round(overall_percentage, 3),
            'improvement_potential': {
                'current_score': round(1.0 + overall_percentage * 3.0, 2),
                'current_level': overall_level.value,
                'target_level': 'Optimized',
                'target_min_score': 4.0,
                'target_max_score': 4.0,
                'gap_to_target': round((1.0 - overall_percentage) * 100, 1),
                'potential_improvement': round((1.0 - overall_percentage) * 100, 1),
                'is_achievable': overall_percentage < 1.0,
            },

            # Detail breakdowns
            'section_scores': section_scores,
            'completion_status': completion,
            'scoring_metadata': {
                'calculation_timestamp': assessment.updated_at,
                'total_responses': len(assessment.responses),
                'scoring_version': '2.0',
            },
        }

        logger.info(
            f"Assessment {assessment_id}: {overall_percentage*100:.1f}% "
            f"({overall_level.value})"
        )
        return results

    # ------------------------------------------------------------------
    # Section scoring
    # ------------------------------------------------------------------

    def _score_all_sections(self, assessment_id: int, allowed_ids: set) -> Dict:
        """Score every active section."""
        sections_q = self.session.query(Section)
        active_ids = _get_active_section_ids(self.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        sections = sections_q.order_by(Section.display_order).all()

        out: Dict = {}
        for section in sections:
            try:
                data = self._score_section(assessment_id, section.id, allowed_ids)
            except Exception as e:
                logger.warning(f"Error scoring section {section.id}: {e}")
                data = self._empty_section()

            out[section.name.lower().replace(' ', '_')] = {
                'section_id': section.id,
                'section_name': section.name,
                'score': data['score'],
                'score_display': format_score_display(data['score']),
                'section_percentage': data.get('section_percentage', 0.0),
                'area_scores': data['area_scores'],
                'coverage': data['coverage'],
                'responses_count': data['responses_count'],
                'total_questions': data['total_questions'],
            }
        return out

    def _score_section(self, assessment_id: int, section_id: str,
                       allowed_ids: set) -> Dict:
        """Score a single section (simple average of its areas)."""
        areas = (
            self.session.query(Area)
            .filter_by(section_id=section_id)
            .order_by(Area.display_order)
            .all()
        )
        if not areas:
            return self._empty_section()

        area_details: Dict = {}
        area_pcts: List[float] = []
        total_resp = 0
        total_qs = 0

        for area in areas:
            ad = self._score_area(assessment_id, area.id, allowed_ids)
            if ad['total_questions'] == 0:
                continue

            area_pcts.append(ad['percentage'])
            total_resp += ad['responses_count']
            total_qs += ad['total_questions']

            area_details[area.name.lower().replace(' ', '_')] = {
                'area_id': area.id,
                'area_name': area.name,
                'score': ad['score'],
                'score_display': format_score_display(ad['score']),
                'domain_normalized': round(ad['percentage'], 3),
                'sse_level': ad['sse_level'].value,
                'area_percentage': round(ad['percentage'], 3),
                'weight': 1.0,
                'responses_count': ad['responses_count'],
                'total_questions': ad['total_questions'],
                'coverage': ad['coverage'],
            }

        section_pct = simple_average(area_pcts)
        section_score = round(1.0 + section_pct * 3.0, 2)
        coverage = calculate_section_coverage(total_resp, total_qs)

        return {
            'score': section_score,
            'section_percentage': section_pct,
            'area_scores': area_details,
            'coverage': coverage,
            'responses_count': total_resp,
            'total_questions': total_qs,
        }

    # ------------------------------------------------------------------
    # Area scoring  (the fundamental unit)
    # ------------------------------------------------------------------

    def _score_area(self, assessment_id: int, area_id: str,
                    allowed_ids: set) -> Dict:
        """
        Score a single area as the simple average of its binary questions.

        percentage = count_of_yes / total_questions
        """
        questions = (
            self.session.query(Question)
            .filter_by(area_id=area_id)
            .order_by(Question.display_order)
            .all()
        )
        questions = [q for q in questions if q.id in allowed_ids and q.is_binary]

        if not questions:
            return {
                'score': 1.0, 'percentage': 0.0, 'sse_level': SSELevel.INFORMAL,
                'weight': 1.0, 'responses_count': 0,
                'total_questions': 0, 'coverage': 0.0,
            }

        yes_count = 0
        responses_count = 0

        for q in questions:
            resp = (
                self.session.query(Response)
                .filter_by(assessment_id=assessment_id, question_id=q.id)
                .first()
            )
            if resp and resp.score is not None:
                responses_count += 1
                if int(resp.score) >= 2:
                    yes_count += 1

        total = len(questions)
        percentage = yes_count / total if total else 0.0
        sse_level = SSEConstants.classify_percentage(percentage)
        score_1to4 = round(1.0 + percentage * 3.0, 2)
        coverage = calculate_section_coverage(responses_count, total)

        return {
            'score': score_1to4,
            'percentage': percentage,
            'sse_level': sse_level,
            'weight': 1.0,
            'responses_count': responses_count,
            'total_questions': total,
            'coverage': coverage,
        }

    # ------------------------------------------------------------------
    # Completion helpers
    # ------------------------------------------------------------------

    def _completion_status(self, assessment_id: int, allowed_ids: set) -> Dict:
        """How many of the allowed questions have been answered?"""
        total = len(allowed_ids)
        answered = (
            self.session.query(Response)
            .filter(
                Response.assessment_id == assessment_id,
                Response.question_id.in_(allowed_ids),
                Response.score.isnot(None),
            )
            .count()
        ) if allowed_ids else 0

        pct = (answered / total * 100) if total else 0

        return {
            'total_questions': total,
            'answered_questions': answered,
            'skipped_questions': 0,
            'unanswered_questions': total - answered,
            'completion_percentage': round(pct, 1),
            'is_complete': pct >= 100.0,
            'is_substantial': pct >= 80.0,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _compute_allowed_question_ids(self) -> set:
        """All active binary question IDs across active sections."""
        sections_q = self.session.query(Section).options(
            joinedload(Section.areas).joinedload(Area.questions)
        )
        active_ids = _get_active_section_ids(self.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        sections = sections_q.order_by(Section.display_order).all()

        ids: set = set()
        for section in sections:
            for area in section.areas:
                for q in area.questions:
                    try:
                        if getattr(q, 'is_active', 1) and q.is_binary:
                            ids.add(q.id)
                    except Exception:
                        continue
        return ids

    @staticmethod
    def _empty_section() -> Dict:
        return {
            'score': 1.0,
            'section_percentage': 0.0,
            'area_scores': {},
            'coverage': 0.0,
            'responses_count': 0,
            'total_questions': 0,
        }
