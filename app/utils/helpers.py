"""
Utility functions for the AI First Maturity Assessment Framework
"""


def get_maturity_level(overall_score):
    """
    Determine the SSE-CMM maturity level based on overall score.

    The score is on a 1.0-4.0 backward-compatible scale where
    1.0 = 0% "Yes" answers and 4.0 = 100% "Yes" answers.
    We convert to a 0-100 percentage and classify via SSE-CMM thresholds.

    Args:
        overall_score (float): The overall assessment score (1.0-4.0)

    Returns:
        dict: Contains level name, description, score range and color
    """
    if overall_score is None:
        return {
            'name': 'Not Assessed',
            'description': 'Assessment not yet completed',
            'range': 'N/A',
            'color': 'secondary'
        }

    # Convert 1.0-4.0 scale to 0-100 percentage
    pct = max(0.0, min(100.0, (overall_score - 1.0) / 3.0 * 100.0))

    if pct <= 20:
        return {
            'name': 'Informal',
            'description': 'Processes are ad-hoc with minimal AI integration',
            'range': '0-20%',
            'color': 'danger'
        }
    elif pct <= 40:
        return {
            'name': 'Defined',
            'description': 'Basic AI practices defined and documented',
            'range': '21-40%',
            'color': 'warning'
        }
    elif pct <= 60:
        return {
            'name': 'Systematic',
            'description': 'Consistent AI integration across key areas',
            'range': '41-60%',
            'color': 'info'
        }
    elif pct <= 80:
        return {
            'name': 'Integrated',
            'description': 'AI deeply embedded into processes and workflows',
            'range': '61-80%',
            'color': 'primary'
        }
    elif pct <= 100:
        return {
            'name': 'Optimized',
            'description': 'AI-native approach with continuous optimization',
            'range': '81-100%',
            'color': 'success'
        }
    else:
        return {
            'name': 'Invalid Score',
            'description': 'Score outside expected range',
            'range': 'Invalid',
            'color': 'secondary'
        }


def format_score_display(overall_score):
    """
    Format the overall score for display with appropriate precision
    
    Args:
        overall_score (float): The overall assessment score
        
    Returns:
        str: Formatted score string
    """
    if overall_score is None:
        return 'N/A'
    
    return f"{overall_score:.1f}"
