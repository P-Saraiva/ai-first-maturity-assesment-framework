"""
Recommendation Service for AFS Assessment Framework
Generates intelligent recommendations based on assessment scores
"""

from typing import Dict, List
from sqlalchemy.orm import Session
import logging

from app.models.assessment import Assessment
from app.services.scoring_service import ScoringService
from app.utils.scoring_utils import classify_maturity_level, ScoringConstants
from app.utils.recommendation_utils import (
    load_recommendation_templates, get_maturity_transition_key,
    generate_recommendation_metadata, rank_recommendations,
    get_next_level_recommendations
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating personalized improvement recommendations
    """

    def __init__(self, session: Session):
        """
        Initialize recommendation service

        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self.scoring_service = ScoringService(session)
        self.recommendation_templates = load_recommendation_templates()

    def generate_assessment_recommendations(self, assessment_id: int,
                                          max_recommendations: int = 20,
                                          include_types: List[str] = None) -> Dict:
        """
        Generate comprehensive recommendations for an assessment

        Args:
            assessment_id: Assessment ID to generate recommendations for
            max_recommendations: Maximum number of recommendations to return
            include_types: Optional list of recommendation types to include

        Returns:
            Dictionary with categorized recommendations

        Raises:
            ValueError: If assessment not found
        """
        try:
            # Get assessment
            assessment = self.session.query(Assessment).filter_by(
                id=assessment_id
            ).first()

            if not assessment:
                raise ValueError(f"Assessment {assessment_id} not found")

            logger.info(f"Generating recommendations for assessment {assessment_id}")

            # Get assessment scoring results
            score_results = self.scoring_service.calculate_assessment_score(
                assessment_id
            )

            # Generate recommendations for each section
            all_recommendations = []
            section_recommendations = {}

            for section_key, section_data in score_results['section_scores'].items():
                section_recs = self._generate_section_recommendations(
                    section_data, score_results['deviq_score']
                )
                all_recommendations.extend(section_recs)
                section_recommendations[section_key] = section_recs

            # Filter by types if specified
            if include_types:
                all_recommendations = [
                    rec for rec in all_recommendations 
                    if rec.get('type') in include_types
                ]

            # Rank and limit recommendations
            ranked_recommendations = rank_recommendations(all_recommendations)
            top_recommendations = ranked_recommendations[:max_recommendations]

            # Categorize recommendations
            categorized = self._categorize_recommendations(top_recommendations)

            # Generate summary
            summary = self._generate_recommendation_summary(
                score_results, top_recommendations
            )

            results = {
                'assessment_id': assessment_id,
                'assessment_name': (assessment.team_name or 
                                  f"Assessment {assessment_id}"),
                'deviq_score': score_results['deviq_score'],
                'maturity_level': score_results['maturity_level_display'],
                'total_recommendations': len(top_recommendations),
                'recommendations': {
                    'all': top_recommendations,
                    'by_section': section_recommendations,
                    'by_type': categorized,
                    'summary': summary
                },
                'improvement_roadmap': self._generate_improvement_roadmap(
                    score_results, top_recommendations
                )
            }

            logger.info(f"Generated {len(top_recommendations)} recommendations "
                       f"for assessment {assessment_id}")

            return results

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    def _generate_section_recommendations(self, section_data: Dict,
                                        overall_deviq: float) -> List[Dict]:
        """
        Generate recommendations for a specific section

        Args:
            section_data: Section scoring data
            overall_deviq: Overall AFS score

        Returns:
            List of recommendations for the section
        """
        section_name = section_data['section_name']
        current_score = section_data['score']
        section_key = section_name.lower().replace(' ', '_')

        # Determine current and target maturity levels
        current_level, _ = classify_maturity_level(current_score)
        overall_level, _ = classify_maturity_level(overall_deviq)

        # Get target level (next level or align with overall assessment)
        target_level_num = get_next_level_recommendations(
            self._maturity_level_to_number(current_level)
        )

        # Get recommendations from templates
        transition_key = get_maturity_transition_key(
            self._maturity_level_to_number(current_level),
            target_level_num
        )

        recommendations = []
        
        try:
            # Get section-specific recommendations
            section_templates = (
                self.recommendation_templates
                .get('recommendations', {})
                .get('level_transitions', {})
                .get(transition_key, {})
                .get(section_key, [])
            )

            target_score = min(ScoringConstants.MAX_SCORE, current_score + 0.8)

            for template in section_templates:
                # Generate metadata for each recommendation
                metadata = generate_recommendation_metadata(
                    template, section_name, current_score, target_score
                )

                recommendation = {
                    'id': f"{section_key}_{len(recommendations) + 1}",
                    'text': template,
                    'section': section_name,
                    'section_key': section_key,
                    'current_level': current_level.name,
                    'target_level': self._number_to_maturity_level(target_level_num).name,
                    **metadata
                }

                recommendations.append(recommendation)

        except Exception as e:
            logger.warning(f"Error generating recommendations for {section_key}: {e}")

        return recommendations

    def _categorize_recommendations(self, recommendations: List[Dict]) -> Dict:
        """
        Categorize recommendations by type

        Args:
            recommendations: List of recommendations

        Returns:
            Dictionary with recommendations categorized by type
        """
        categorized = {
            'quick_wins': [],
            'foundational': [],
            'strategic': [],
            'transformational': []
        }

        for rec in recommendations:
            rec_type = rec.get('type', 'foundational')
            if rec_type == 'quick_win':
                categorized['quick_wins'].append(rec)
            elif rec_type == 'foundational':
                categorized['foundational'].append(rec)
            elif rec_type == 'strategic':
                categorized['strategic'].append(rec)
            elif rec_type == 'transformational':
                categorized['transformational'].append(rec)

        return categorized

    def _generate_recommendation_summary(self, score_results: Dict,
                                       recommendations: List[Dict]) -> Dict:
        """
        Generate a summary of recommendations

        Args:
            score_results: Assessment scoring results
            recommendations: List of recommendations

        Returns:
            Dictionary with recommendation summary
        """
        if not recommendations:
            return {
                'total_count': 0,
                'by_priority': {'high': 0, 'medium': 0, 'low': 0},
                'by_type': {'quick_win': 0, 'foundational': 0, 'strategic': 0, 'transformational': 0},
                'estimated_effort': {'time_weeks': 0, 'resources_needed': 0}
            }

        # Count by priority
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Count by type
        type_counts = {'quick_win': 0, 'foundational': 0, 'strategic': 0, 'transformational': 0}
        for rec in recommendations:
            rec_type = rec.get('type', 'foundational')
            type_counts[rec_type] = type_counts.get(rec_type, 0) + 1

        # Calculate total effort
        total_time = sum(
            rec.get('effort_estimate', {}).get('time_weeks', 0)
            for rec in recommendations
        )
        total_resources = sum(
            rec.get('effort_estimate', {}).get('resources_needed', 0)
            for rec in recommendations
        )

        return {
            'total_count': len(recommendations),
            'by_priority': priority_counts,
            'by_type': type_counts,
            'estimated_effort': {
                'time_weeks': total_time,
                'resources_needed': total_resources
            },
            'current_maturity': score_results['maturity_level_display'],
            'deviq_score': score_results['deviq_score'],
            'improvement_potential': score_results['improvement_potential']['gap_to_target']
        }

    def _generate_improvement_roadmap(self, score_results: Dict,
                                    recommendations: List[Dict]) -> Dict:
        """
        Generate an improvement roadmap

        Args:
            score_results: Assessment scoring results
            recommendations: List of recommendations

        Returns:
            Dictionary with improvement roadmap
        """
        # Group recommendations by priority and type
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        quick_wins = [r for r in recommendations if r.get('type') == 'quick_win']
        foundational = [r for r in recommendations if r.get('type') == 'foundational']

        roadmap = {
            'current_state': {
                'deviq_score': score_results['deviq_score'],
                'maturity_level': score_results['maturity_level_display'],
                'completion_rate': score_results['completion_status']['completion_percentage']
            },
            'immediate_actions': {
                'description': 'High-priority recommendations to implement first',
                'recommendations': high_priority[:5],
                'estimated_duration': '2-4 weeks'
            },
            'quick_wins': {
                'description': 'Low-effort, high-impact improvements',
                'recommendations': quick_wins[:3],
                'estimated_duration': '1-2 weeks'
            },
            'foundational_improvements': {
                'description': 'Core capability building initiatives',
                'recommendations': foundational[:5],
                'estimated_duration': '2-3 months'
            },
            'target_state': {
                'target_level': score_results['improvement_potential']['target_level'],
                'target_score': score_results['improvement_potential']['target_min_score'],
                'estimated_timeline': '6-12 months'
            }
        }

        return roadmap

    def get_recommendations_by_section(self, assessment_id: int,
                                     section_name: str) -> List[Dict]:
        """
        Get recommendations for a specific section

        Args:
            assessment_id: Assessment ID
            section_name: Name of the section

        Returns:
            List of recommendations for the section
        """
        results = self.generate_assessment_recommendations(assessment_id)
        section_key = section_name.lower().replace(' ', '_')
        
        return results['recommendations']['by_section'].get(section_key, [])

    def get_quick_wins(self, assessment_id: int, limit: int = 10) -> List[Dict]:
        """
        Get quick win recommendations

        Args:
            assessment_id: Assessment ID
            limit: Maximum number of quick wins to return

        Returns:
            List of quick win recommendations
        """
        results = self.generate_assessment_recommendations(
            assessment_id, 
            include_types=['quick_win']
        )
        
        return results['recommendations']['by_type']['quick_wins'][:limit]

    def get_priority_recommendations(self, assessment_id: int,
                                   priority: str = 'high',
                                   limit: int = 10) -> List[Dict]:
        """
        Get recommendations by priority level

        Args:
            assessment_id: Assessment ID
            priority: Priority level ('high', 'medium', 'low')
            limit: Maximum number of recommendations

        Returns:
            List of priority recommendations
        """
        results = self.generate_assessment_recommendations(assessment_id)
        priority_recs = [
            rec for rec in results['recommendations']['all']
            if rec.get('priority') == priority
        ]
        
        return priority_recs[:limit]

    def _maturity_level_to_number(self, level) -> int:
        """Convert SSE maturity level enum to number (1-5)"""
        level_map = {
            'INFORMAL': 1,
            'DEFINED': 2,
            'SYSTEMATIC': 3,
            'INTEGRATED': 4,
            'OPTIMIZED': 5,
        }
        return level_map.get(level.name, 1)

    def _number_to_maturity_level(self, number: int):
        """Convert number to SSE maturity level enum"""
        from app.utils.scoring_utils import SSELevel

        level_map = {
            1: SSELevel.INFORMAL,
            2: SSELevel.DEFINED,
            3: SSELevel.SYSTEMATIC,
            4: SSELevel.INTEGRATED,
            5: SSELevel.OPTIMIZED,
        }
        return level_map.get(number, SSELevel.INFORMAL)
