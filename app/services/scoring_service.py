"""
Scoring Service for AFS Assessment Framework
Calculates AFS scores and maturity classifications
"""

from typing import Dict, List
from sqlalchemy.orm import Session
import logging

from app.models.assessment import Assessment
from app.models.response import Response
from app.models.question import Question, Section, Area
from app.utils.scoring_utils import (
    ScoringConstants,
    SSEConstants, SSELevel,
    calculate_weighted_average,
    classify_maturity_level, get_maturity_level_details,
    calculate_section_coverage, validate_score_inputs,
    format_score_display, calculate_improvement_potential
)

logger = logging.getLogger(__name__)

ALLOWED_SECTION_IDS = ['FC', 'TC', 'EI']


class ScoringService:
    """
    Main service for calculating AFS scores and maturity classifications
    """

    def __init__(self, session: Session):
        """
        Initialize scoring service with database session

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def calculate_assessment_score(self, assessment_id: int) -> Dict:
        """
        Calculate complete assessment score including DevIQ and maturity level

        Args:
            assessment_id: Assessment ID to score

        Returns:
            Dictionary with complete scoring results

        Raises:
            ValueError: If assessment not found or invalid
        """
        try:
            # Get assessment
            assessment = self.session.query(Assessment).filter_by(
                id=assessment_id
            ).first()

            if not assessment:
                raise ValueError(f"Assessment {assessment_id} not found")

            logger.info(f"Calculating score for assessment {assessment_id}")

            # Calculate section scores
            section_scores = self._calculate_section_scores(assessment_id)

            # Legacy overall AFS score (1.0-4.0) for backward compatibility
            deviq_score = self._calculate_deviq_score(section_scores)
            # Map to normalized 0..1
            overall_normalized = max(0.0, min(1.0, (deviq_score - 1.0) / 3.0))

            # SSE overall percentage = weighted average of area percentages
            all_area_percentages = []
            all_area_weights = []
            for sec in section_scores.values():
                for area_key, a in sec['area_scores'].items():
                    pct = a.get('area_percentage')
                    w = SSEConstants.AREA_WEIGHTS.get(a['area_id'], a.get('weight', 1.0))
                    if pct is not None:
                        all_area_percentages.append(pct)
                        all_area_weights.append(w)
            overall_percentage = 0.0
            if all_area_percentages:
                overall_percentage = calculate_weighted_average(all_area_percentages, all_area_weights)
            overall_sse_level = SSEConstants.classify_percentage(overall_percentage)

            # Get detailed results
            results = {
                'assessment_id': assessment_id,
                'assessment_name': (assessment.team_name or 
                                  f"Assessment {assessment_id}"),
                'deviq_score': deviq_score,
                'deviq_score_display': format_score_display(deviq_score),
                'maturity_level': overall_sse_level.name,
                'maturity_level_display': overall_sse_level.value,
                'maturity_details': SSEConstants.get_level_details(overall_sse_level),
                'section_scores': section_scores,
                'overall_normalized': round(overall_normalized, 3),
                'overall_percentage': round(overall_percentage, 3),
                'improvement_potential': calculate_improvement_potential(
                    deviq_score
                ),
                'completion_status': self._calculate_completion_status(
                    assessment_id
                ),
                'scoring_metadata': {
                    'calculation_timestamp': assessment.updated_at,
                    'total_responses': len(assessment.responses),
                    'scoring_version': '1.0'
                }
            }

            logger.info(
                f"Assessment {assessment_id} scored: DevIQ {deviq_score}, "
                f"Level: {overall_sse_level.value}"
            )

            return results

        except Exception as e:
            logger.error(f"Error calculating assessment score: {e}")
            raise

    def _calculate_section_scores(self, assessment_id: int) -> Dict:
        """
        Calculate scores for each section in the assessment

        Args:
            assessment_id: Assessment ID

        Returns:
            Dictionary with section scores and details
        """
        section_scores = {}

        # Get all sections
        sections = self.session.query(Section).filter(
            Section.id.in_(ALLOWED_SECTION_IDS)
        ).order_by(Section.display_order).all()

        allowed_ids = self._compute_allowed_question_ids()

        for section in sections:
            try:
                score_data = self._calculate_single_section_score(
                    assessment_id, section.id, allowed_ids
                )
                section_scores[section.name.lower().replace(' ', '_')] = {
                    'section_id': section.id,
                    'section_name': section.name,
                    'score': score_data['score'],
                    'score_display': format_score_display(score_data['score']),
                    'area_scores': score_data['area_scores'],
                    'coverage': score_data['coverage'],
                    'responses_count': score_data['responses_count'],
                    'total_questions': score_data['total_questions']
                }

            except Exception as e:
                logger.warning(f"Error calculating section {section.id}: {e}")
                # Set default values for failed section
                section_scores[section.name.lower().replace(' ', '_')] = {
                    'section_id': section.id,
                    'section_name': section.name,
                    'score': ScoringConstants.MIN_SCORE,
                    'score_display': format_score_display(
                        ScoringConstants.MIN_SCORE
                    ),
                    'area_scores': {},
                    'coverage': 0.0,
                    'responses_count': 0,
                    'total_questions': 0,
                    'error': str(e)
                }

        return section_scores

    def _calculate_single_section_score(self, assessment_id: int,
                                       section_id: int,
                                       allowed_ids: set) -> Dict:
        """
        Calculate score for a single section

        Args:
            assessment_id: Assessment ID
            section_id: Section ID

        Returns:
            Dictionary with section score details
        """
        # Get all areas in this section
        areas = self.session.query(Area).filter_by(
            section_id=section_id
        ).order_by(Area.display_order).all()

        if not areas:
            return {
                'score': ScoringConstants.MIN_SCORE,
                'area_scores': {},
                'coverage': 0.0,
                'responses_count': 0,
                'total_questions': 0
            }

        area_scores = []  # legacy 1..4 mapping
        area_weights = []
        area_details = {}
        total_responses = 0
        total_questions = 0

        for area in areas:
            area_data = self._calculate_area_score(assessment_id, area.id, allowed_ids)
            # Skip areas without allowed questions
            if area_data['total_questions'] == 0:
                continue
            area_scores.append(area_data['score'])
            area_weights.append(area_data['weight'])

            area_details[area.name.lower().replace(' ', '_')] = {
                'area_id': area.id,
                'area_name': area.name,
                'score': area_data['score'],
                'score_display': format_score_display(area_data['score']),
                'domain_normalized': round(area_data['normalized'], 3),
                'sse_level': area_data['sse_level'].value,
                'area_percentage': round(area_data['percentage'], 3),
                'weight': area_data['weight'],
                'responses_count': area_data['responses_count'],
                'total_questions': area_data['total_questions'],
                'coverage': area_data['coverage']
            }

            total_responses += area_data['responses_count']
            total_questions += area_data['total_questions']

        # Calculate section score as weighted average of area scores
        if area_scores:
            validate_score_inputs(area_scores, area_weights)
            section_score = calculate_weighted_average(area_scores,
                                                      area_weights)
        else:
            section_score = ScoringConstants.MIN_SCORE

        # Calculate overall coverage
        coverage = calculate_section_coverage(total_responses, total_questions)

        return {
            'score': section_score,
            'area_scores': area_details,
            'coverage': coverage,
            'responses_count': total_responses,
            'total_questions': total_questions
        }

    def _calculate_area_score(self, assessment_id: int, area_id: int, allowed_ids: set) -> Dict:
        """
        Calculate score for a single area

        Args:
            assessment_id: Assessment ID
            area_id: Area ID

        Returns:
            Dictionary with area score details
        """
        # Get all questions in this area with their responses
        questions = self.session.query(Question).filter_by(
            area_id=area_id
        ).order_by(Question.display_order).all()

        # Filter to allowed questions only
        questions = [q for q in questions if q.id in allowed_ids]

        if not questions:
            return {
                'score': ScoringConstants.MIN_SCORE,
                'normalized': 0.0,
                'domain_level': 1,
                'weight': 1.0,
                'responses_count': 0,
                'total_questions': 0,
                'coverage': 0.0
            }

        # New binary weighted scoring per domain (area)
        total_weight = 0.0
        weighted_yes = 0.0
        responses_count = 0

        # Track dependency data per level
        level_weights = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        level_yes_weights = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}

        for q in questions:
            # Only consider binary questions
            if not q.is_binary:
                continue

            w = float(getattr(q, 'binary_weight', 1.0) or 1.0)
            lvl = int(getattr(q, 'binary_level', 1) or 1)

            total_weight += w
            level_weights[lvl] += w

            resp = self.session.query(Response).filter_by(
                assessment_id=assessment_id,
                question_id=q.id
            ).first()

            if resp and resp.score is not None:
                responses_count += 1
                # Map 1 (No) -> 0, 2 (Yes) -> 1
                ans = 1.0 if float(resp.score) >= 2.0 else 0.0
            else:
                ans = 0.0

            weighted_yes += ans * w
            if ans > 0.0:
                level_yes_weights[lvl] += w

        if total_weight <= 0.0:
            normalized = 0.0
        else:
            normalized = max(0.0, min(1.0, weighted_yes / total_weight))

        # Infer domain maturity level from normalized score
        if normalized <= 0.25:
            inferred_level = 1
        elif normalized <= 0.50:
            inferred_level = 2
        elif normalized <= 0.75:
            inferred_level = 3
        else:
            inferred_level = 4

        # Enforce dependency rule: cannot reach level N if lower levels < X%
        DEP_THRESHOLD = 0.7  # 70% by default; can be made configurable
        def lower_levels_satisfied(target_level: int) -> bool:
            if target_level <= 1:
                return True
            total_lower = sum(level_weights[l] for l in range(1, target_level))
            if total_lower <= 0:
                return True
            yes_lower = sum(level_yes_weights[l] for l in range(1, target_level))
            return (yes_lower / total_lower) >= DEP_THRESHOLD

        domain_level = inferred_level
        while domain_level > 1 and not lower_levels_satisfied(domain_level):
            domain_level -= 1

        # Map normalized (0..1) to 1.0-4.0 scale for backwards compatibility
        area_score_1to4 = 1.0 + (normalized * 3.0)

        # Coverage = answered binary questions / total binary questions in area
        total_binary_questions = sum(1 for q in questions if q.is_binary)
        coverage = calculate_section_coverage(responses_count, total_binary_questions)

        # Percentage of confirmed capabilities (Yes answers)
        percentage_yes = normalized  # normalized already 0..1 of weighted yes
        sse_level = SSEConstants.classify_percentage(percentage_yes)

        return {
            'score': area_score_1to4,
            'normalized': percentage_yes,
            'sse_level': sse_level,
            'percentage': percentage_yes,
            'weight': 1.0,  # Equal weighting for areas within sections
            'responses_count': responses_count,
            'total_questions': total_binary_questions,
            'coverage': coverage
        }

    def _compute_allowed_question_ids(self) -> set:
        """Compute the set of question IDs considered for scoring.
        Include all active binary questions in allowed sections.
        """
        from sqlalchemy.orm import joinedload
        allowed_ids: set = set()
        sections = self.session.query(Section).options(
            joinedload(Section.areas).joinedload(Area.questions)
        ).filter(Section.id.in_(ALLOWED_SECTION_IDS)).order_by(Section.display_order).all()

        for section in sections:
            for area in section.areas:
                for q in area.questions:
                    try:
                        if getattr(q, 'is_active', 1) and q.is_binary:
                            allowed_ids.add(q.id)
                    except Exception:
                        continue
        return allowed_ids

    def _calculate_deviq_score(self, section_scores: Dict) -> float:
        """
        Calculate overall AFS score from section scores

        Args:
            section_scores: Dictionary of section scores

        Returns:
            Overall AFS score (1.0-4.0)
        """
        if not section_scores:
            return ScoringConstants.MIN_SCORE

        scores = []
        weights = []

        # Extract scores and weights for each section
        for section_key, section_data in section_scores.items():
            if 'score' in section_data and section_data['score'] is not None:
                scores.append(section_data['score'])
                # Use predefined weights or default to equal weighting
                weight = SSEConstants.SECTION_WEIGHTS.get(
                    section_key, 0.25
                )
                weights.append(weight)

        if not scores:
            return ScoringConstants.MIN_SCORE

        # Validate and calculate weighted average
        validate_score_inputs(scores, weights)
        deviq_score = calculate_weighted_average(scores, weights)

        # Ensure score is within valid range
        deviq_score = max(ScoringConstants.MIN_SCORE,
                         min(ScoringConstants.MAX_SCORE, deviq_score))

        return round(deviq_score, 2)

    def _calculate_completion_status(self, assessment_id: int) -> Dict:
        """
        Calculate assessment completion status

        Args:
            assessment_id: Assessment ID

        Returns:
            Dictionary with completion statistics
        """
        allowed_ids = self._compute_allowed_question_ids()

        # Determine logical questions: one per binary group and one per multi-level
        # Build groups
        binary_groups = {}
        single_questions = []
        for qid in allowed_ids:
            if qid[-1] in 'ABCDEF' and qid[:-1][-2:].isdigit():
                base = qid[:-1]
                binary_groups.setdefault(base, []).append(qid)
            else:
                single_questions.append(qid)

        total_questions = len(binary_groups) + len(single_questions)

        # Count answered logical questions
        answered_questions = 0
        # Binary groups: count 1 if any sub-question answered
        for base, members in binary_groups.items():
            resp = self.session.query(Response).filter(
                Response.assessment_id == assessment_id,
                Response.question_id.in_(members),
                Response.score.isnot(None)
            ).first()
            if resp:
                answered_questions += 1
        # Single questions
        if single_questions:
            count_single = self.session.query(Response).filter(
                Response.assessment_id == assessment_id,
                Response.question_id.in_(single_questions),
                Response.score.isnot(None)
            ).count()
            answered_questions += count_single

        # Calculate percentages
        completion_percentage = (answered_questions / total_questions * 100
                               if total_questions > 0 else 0)

        return {
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'skipped_questions': 0,  # Not tracked in current schema
            'unanswered_questions': total_questions - answered_questions,
            'completion_percentage': round(completion_percentage, 1),
            'is_complete': completion_percentage >= 100.0,
            'is_substantial': completion_percentage >= 80.0  # 80% threshold
        }

    def get_section_benchmark(self, section_name: str) -> Dict:
        """
        Get benchmark data for a specific section

        Args:
            section_name: Name of the section

        Returns:
            Dictionary with benchmark information
        """
        # Industry benchmark data (would typically come from database)
        benchmarks = {
            'foundational_capabilities': {
                'industry_average': 2.1,
                'top_quartile': 2.8,
                'best_in_class': 3.5
            },
            'transformation_capabilities': {
                'industry_average': 1.9,
                'top_quartile': 2.6,
                'best_in_class': 3.3
            },
            'enterprise_integration': {
                'industry_average': 1.7,
                'top_quartile': 2.4,
                'best_in_class': 3.1
            },
            'strategic_governance': {
                'industry_average': 1.6,
                'top_quartile': 2.3,
                'best_in_class': 3.0
            }
        }

        section_key = section_name.lower().replace(' ', '_')
        return benchmarks.get(section_key, {
            'industry_average': 2.0,
            'top_quartile': 2.5,
            'best_in_class': 3.2
        })

    def calculate_score_trends(self, assessment_ids: List[int]) -> Dict:
        """
        Calculate scoring trends across multiple assessments

        Args:
            assessment_ids: List of assessment IDs to analyze

        Returns:
            Dictionary with trend analysis
        """
        if not assessment_ids:
            return {}

        trends = {
            'assessment_count': len(assessment_ids),
            'deviq_scores': [],
            'maturity_levels': [],
            'section_trends': {}
        }

        for assessment_id in assessment_ids:
            try:
                score_data = self.calculate_assessment_score(assessment_id)
                trends['deviq_scores'].append(score_data['deviq_score'])
                trends['maturity_levels'].append(
                    score_data['maturity_level']
                )

                # Track section trends
                for section_key, section_data in score_data[
                    'section_scores'
                ].items():
                    if section_key not in trends['section_trends']:
                        trends['section_trends'][section_key] = []
                    trends['section_trends'][section_key].append(
                        section_data['score']
                    )

            except Exception as e:
                logger.warning(f"Error processing assessment {assessment_id} "
                              f"for trends: {e}")

        return trends
