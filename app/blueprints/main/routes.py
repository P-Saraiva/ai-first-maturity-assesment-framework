"""
Main blueprint routes for AFS Assessment Framework
"""
from flask import Blueprint, render_template, jsonify
from sqlalchemy import func, text
from datetime import datetime

from app.models import Assessment, Section, Area, Question
from app.core.logging import get_logger

logger = get_logger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page with statistics and recent activity
    """
    try:
        # Get database session
        from app.extensions import db
        
        # Calculate homepage statistics
        total_assessments = db.session.query(
            func.count(Assessment.id)
        ).scalar() or 0
        unique_organizations = db.session.execute(
            text('SELECT COUNT(DISTINCT team_name) FROM assessments '
                 'WHERE team_name IS NOT NULL')
        ).scalar() or 0
        
        # Calculate completed assessments for better metrics
        completed_assessments = db.session.execute(
            text("SELECT * FROM assessments WHERE status = 'COMPLETED'")
        ).fetchall()
        
        # Calculate average AFS score
        average_deviq = 0
        if completed_assessments:
            deviq_scores = []
            for assessment in completed_assessments:
                if (hasattr(assessment, 'overall_score') and
                        assessment.overall_score):
                    deviq_scores.append(assessment.overall_score)
            if deviq_scores:
                average_deviq = sum(deviq_scores) / len(deviq_scores)
        
        # Calculate completion rate
        completion_rate = 0
        if total_assessments > 0:
            completed_count = len(completed_assessments)
            completion_rate = (completed_count / total_assessments) * 100
        
        # Get recent assessments (last 10)
        recent_assessments = db.session.execute(
            text("SELECT * FROM assessments "
            "WHERE status IN ('COMPLETED', 'IN_PROGRESS') "
            "ORDER BY updated_at DESC LIMIT 10")
        ).fetchall()
        
        # Calculate average improvement (simulated for demo)
        average_improvement = 23.5  # Would be calculated from historical data
        
        # Calculate average completion time (simulated)
        avg_completion_time = 28  # Would be calculated from actual data
        
        # DevIQ improvement (simulated for demo)
        deviq_improvement = 15.2  # Would be calculated from time series data
        
        # Prepare template context
        context = {
            'total_assessments': total_assessments,
            'unique_organizations': unique_organizations,
            'average_deviq': average_deviq,
            'completion_rate': completion_rate,
            'average_improvement': average_improvement,
            'avg_completion_time': avg_completion_time,
            'deviq_improvement': deviq_improvement,
            'recent_assessments': recent_assessments
        }
        
        return render_template('pages/home/index.html', **context)
        
    except Exception as e:
        logger.error(f"Error rendering home page: {e}")
        # Return basic template on error
        return render_template('pages/home/index.html')


@main_bp.route('/about')
def about():
    """
    About page with framework information
    """
    try:
        # Get framework statistics
        from app.extensions import db
        
        # Count framework components
        total_sections = db.session.query(func.count(Section.id)).scalar() or 0
        total_areas = db.session.query(func.count(Area.id)).scalar() or 0
        total_questions = db.session.query(
            func.count(Question.id)
        ).scalar() or 0
        
        # Get sections with their areas for display
        sections = db.session.query(Section).options(
            db.joinedload(Section.areas)
        ).order_by(Section.display_order).all()
        
        context = {
            'total_sections': total_sections,
            'total_areas': total_areas,
            'total_questions': total_questions,
            'sections': sections,
            'framework_version': '1.0',
            'last_updated': datetime.now().strftime('%B %Y')
        }
        
        return render_template('pages/home/about.html', **context)
        
    except Exception as e:
        logger.error(f"Error rendering about page: {e}")
        return render_template('pages/home/about.html')


@main_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check database connection
        from app.extensions import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'database': 'healthy',
                'application': 'healthy'
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500


@main_bp.route('/health/write')
def health_check_write():
    """Health check that verifies database write capability.

    Attempts to create a small table, insert a row, and then clean it up.
    If any step fails, returns unhealthy with the error.
    """
    from flask import current_app
    try:
        from app.extensions import db
        from sqlalchemy import text

        # Create table if not exists
        db.session.execute(text('CREATE TABLE IF NOT EXISTS health_write_test (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT)'))
        # Insert a row
        db.session.execute(text("INSERT INTO health_write_test (ts) VALUES (:ts)"), { 'ts': datetime.utcnow().isoformat() })
        db.session.commit()

        # Optional cleanup: keep small footprint by deleting older rows
        db.session.execute(text("DELETE FROM health_write_test WHERE id < (SELECT IFNULL(MAX(id),0) FROM health_write_test)"))
        db.session.commit()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'database_write': 'healthy'
            }
        })
    except Exception as e:
        current_app.logger.error(f"Write health check failed: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500


@main_bp.route('/api/config')
def api_config():
    """
    API endpoint for application configuration
    """
    try:
        config = {
            'debug': False,
            'apiTimeout': 30000,
            'autoSaveInterval': 30000,
            'chartRefreshInterval': 300000,
            'maxRetries': 3,
            'retryDelay': 1000,
            'version': '2.0.0',
            'features': {
                'analytics': True,
                'export': True,
                'notifications': True,
                'darkMode': True
            },
            'widgets': {
                'dashboard': ['stats', 'charts', 'recent'],
                'assessment': ['progress', 'recommendations'],
                'analytics': ['trends', 'comparisons']
            }
        }
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch configuration'
        }), 500


@main_bp.route('/api/stats')
def api_stats():
    """
    API endpoint for homepage statistics
    """
    try:
        from app.extensions import db
        
        # Get basic statistics using direct database queries
        total_assessments = db.session.query(
            func.count(Assessment.id)
        ).scalar() or 0
        
        completed_assessments = db.session.query(Assessment).filter(
            Assessment.status == 'COMPLETED'
        ).count()
        
        in_progress_assessments = db.session.query(Assessment).filter(
            Assessment.status == 'IN_PROGRESS'
        ).count()
        
        total_questions = db.session.query(Question).count()
        
        # Calculate average score for completed assessments
        completed_with_scores = db.session.query(Assessment).filter(
            Assessment.status == 'COMPLETED',
            Assessment.overall_score.isnot(None)
        ).all()
        
        average_score = 0
        if completed_with_scores:
            scores = [
                a.overall_score for a in completed_with_scores
                if a.overall_score
            ]
            if scores:
                average_score = sum(scores) / len(scores)
        
        stats = {
            'total_assessments': total_assessments,
            'completed_assessments': completed_assessments,
            'in_progress_assessments': in_progress_assessments,
            'total_questions': total_questions,
            'average_score': round(average_score, 2)
        }
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch statistics',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    from app.extensions import db
    db.session.rollback()
    return render_template('errors/500.html'), 500
