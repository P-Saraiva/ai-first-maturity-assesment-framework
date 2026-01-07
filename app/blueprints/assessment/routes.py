"""
Assessment blueprint routes for AFS Assessment Framework
"""

import json
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    jsonify, session, current_app, make_response
)
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.models import Assessment, Section, Area, Question, Response
from app.services.assessment_service import AssessmentService
from app.services.scoring_service import ScoringService
from app.services.recommendation_service import RecommendationService
from app.utils.exceptions import AssessmentError, ValidationError
from app.utils.helpers import get_maturity_level, format_score_display
from app.core.logging import get_logger
from app.extensions import csrf

logger = get_logger(__name__)

assessment_bp = Blueprint('assessment', __name__, url_prefix='/assessment')

def _get_active_section_ids(db_session=None):
    """Return list of active section IDs.

    Order preference:
    - If Flask config ACTIVE_SECTION_IDS is set (comma-separated), use it.
    - Else, use env var ACTIVE_SECTION_IDS.
    - Else, load all section IDs ordered by display_order from DB.
    """
    import os
    ids = None
    try:
        env_val = current_app.config.get('ACTIVE_SECTION_IDS')
        if isinstance(env_val, str) and env_val.strip():
            ids = [s.strip() for s in env_val.split(',') if s.strip()]
        elif isinstance(env_val, (list, tuple)) and env_val:
            ids = [str(s).strip() for s in env_val if str(s).strip()]
    except Exception:
        pass
    if ids is None:
        env_val = os.environ.get('ACTIVE_SECTION_IDS')
        if env_val:
            ids = [s.strip() for s in env_val.split(',') if s.strip()]
    if ids is None and db_session is not None:
        try:
            ids = [s.id for s in db_session.query(Section).order_by(Section.display_order).all()]
        except Exception:
            ids = []
    return ids or []
# Limit assessment to seeded sections in linear flow
# Must match IDs present in scripts/database_seed_data.sql: FC, TC, EI, SG
# Keeping to core three for initial flow
ALLOWED_SECTION_IDS = ['FC', 'TC', 'EI', 'SG']

def _compute_allowed_question_ids(db_session):
    """Include all active binary checklist question IDs across allowed sections.
    Returns (allowed_ids_set, binary_groups_map_by_base).
    """
    sections = db_session.query(Section).options(
        joinedload(Section.areas).joinedload(Area.questions)
    )
    # Optionally filter by active section ids
    active_ids = _get_active_section_ids(db_session)
    if active_ids:
        sections = sections.filter(Section.id.in_(active_ids))
    sections = sections.order_by(Section.display_order).all()
    allowed_ids = set()
    binary_groups = {}
    for section in sections:
        for area in section.areas:
            for q in area.questions:
                try:
                    if getattr(q, 'is_active', 1) and q.is_binary:
                        allowed_ids.add(q.id)
                        # Group by base id (strip A-F suffix)
                        if isinstance(q.id, str) and q.id and q.id[-1] in 'ABCDEF' and q.id[:-1][-2:].isdigit():
                            base = q.id[:-1]
                            binary_groups.setdefault(base, []).append(q.id)
                except Exception:
                    continue
    # Ensure members are sorted for deterministic behavior
    for base in list(binary_groups.keys()):
        binary_groups[base] = sorted(binary_groups[base])
    return allowed_ids, binary_groups


def get_assessment_service():
    """Get assessment service instance with current database session"""
    from app.extensions import db
    return AssessmentService(db.session)


def get_scoring_service():
    """Get scoring service instance with current database session"""
    from app.extensions import db
    return ScoringService(db.session)


def get_recommendation_service():
    """Get recommendation service instance with current database session"""
    from app.extensions import db
    return RecommendationService(db.session)


def format_industry(industry_code):
    """Format industry code to human readable name"""
    industry_mapping = {
        'automotive': 'Automotive',
        'bfsi': 'Banking, Financial Services & Insurance',
        'energy_utilities': 'Energy & Utilities',
        'government': 'Government & Public Sector',
        'travel_transport_tourism': 'Travel, Transport & Tourism',
        'healthcare': 'Healthcare',
        'media_communications': 'Media & Communications',
        'retail_commerce': 'Retail & Commerce',
        'technology': 'Technology',
        'other': 'Other'
    }
    return industry_mapping.get(industry_code, industry_code.title())


def manage_assessment_session(assessment_id):
    """
    Manage assessment session state for user navigation
    
    Args:
        assessment_id: Assessment ID to track in session
    """
    session['current_assessment_id'] = assessment_id
    session['assessment_start_time'] = datetime.utcnow().isoformat()
    session.permanent = True  # Keep session across browser restarts


def get_current_assessment():
    """
    Get current assessment from session if available
    
    Returns:
        Assessment ID or None
    """
    return session.get('current_assessment_id')


def clear_assessment_session():
    """Clear assessment-related session data"""
    session.pop('current_assessment_id', None)
    session.pop('assessment_start_time', None)
    session.pop('assessment_responses', None)
    session.pop('assessment_metadata', None)


def validate_assessment_session(assessment_id):
    """
    Validate that the session assessment matches the requested assessment
    
    Args:
        assessment_id: Assessment ID to validate against session
    
    Returns:
        bool: True if session is valid, False otherwise
    """
    current_assessment = get_current_assessment()
    if current_assessment and current_assessment != assessment_id:
        return False
    return True


def update_session_activity():
    """Update session activity timestamp"""
    session['last_activity'] = datetime.utcnow().isoformat()


@assessment_bp.before_request
def before_assessment_request():
    """
    Pre-request processing for assessment routes
    """
    # Update session activity for assessment routes
    update_session_activity()
    
    # Set session timeout (optional - extend session for active users)
    session.permanent = True


@assessment_bp.errorhandler(404)
def assessment_not_found(error):
    """Handle 404 errors in assessment blueprint"""
    flash('The requested assessment or page was not found.', 'error')
    return redirect(url_for('assessment.index'))


@assessment_bp.errorhandler(500)
def assessment_server_error(error):
    """Handle 500 errors in assessment blueprint"""
    logger.error(f"Server error in assessment blueprint: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('assessment.index'))


@assessment_bp.route('/')
def index():
    """
    Enhanced assessment overview page with search, filtering, and grid view
    """
    try:
        from app.extensions import db
        from sqlalchemy import or_, and_
        
        # Get search and filter parameters
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to = request.args.get('date_to', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        # Build query with filters
        query = db.session.query(Assessment).filter(
            Assessment.status.isnot(None)
        )
        
        # Apply search filter
        if search_query:
            query = query.filter(
                or_(
                    Assessment.team_name.ilike(f'%{search_query}%'),
                    Assessment.id.like(f'%{search_query}%')
                )
            )
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            query = query.filter(Assessment.status == status_filter)
        
        # Apply date filters
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Assessment.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Assessment.created_at <= date_to_obj)
            except ValueError:
                pass
        
        # Order by most recent
        query = query.order_by(Assessment.updated_at.desc())
        
        # Paginate results
        assessments_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        assessments = assessments_pagination.items
        
        # Add maturity levels to assessments
        for assessment in assessments:
            maturity = get_maturity_level(assessment.overall_score)
            assessment.maturity_level = maturity
        
        # Get framework statistics (constrained logical question count)
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        total_questions = len(bin_groups) + (len(allowed_ids) - sum(len(m) for m in bin_groups.values()))
        # Only show active sections
        sections_q = db.session.query(Section)
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        sections = sections_q.order_by(Section.display_order).all()
        
        # Get assessment statistics
        total_assessments = db.session.query(Assessment).filter(
            Assessment.status.isnot(None)
        ).count()
        completed_assessments = db.session.query(Assessment).filter(
            Assessment.status == 'COMPLETED'
        ).count()
        in_progress_assessments = db.session.query(Assessment).filter(
            Assessment.status == 'IN_PROGRESS'
        ).count()
        
        # Get unique statuses for filter dropdown
        status_options = db.session.query(Assessment.status).filter(
            Assessment.status.isnot(None)
        ).distinct().all()
        status_options = [status[0] for status in status_options if status[0]]
        
        context = {
            'assessments': assessments,
            'pagination': assessments_pagination,
            'total_questions': total_questions,
            'sections': sections or [],
            'total_sections': len(sections),
            'total_assessments': total_assessments,
            'completed_assessments': completed_assessments,
            'in_progress_assessments': in_progress_assessments,
            'status_options': status_options,
            'search_query': search_query,
            'status_filter': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'current_page': page,
            'per_page': per_page
        }
        
        return render_template('pages/assessment/index.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading assessment index: {e}")
        flash('Error loading assessments', 'error')
        # Provide safe defaults
        return render_template('pages/assessment/index.html', 
                       assessments=[], 
                       sections=[], 
                       total_questions=0,
                       total_sections=0)


@assessment_bp.route('/create', methods=['GET', 'POST'])
def create():
    """
    Simplified Linear Assessment Creation Flow
    Step 1: Collect organization + candidate details, then proceed directly to first section
    """
    if request.method == 'GET':
        # Show the organization and candidate information form
        return render_template('pages/assessment/org_information.html')
    
    # POST method - from form submission
    try:
        # Get form data for organization and candidate
        organization_name = request.form.get('organization_name', '').strip()
        account_name = request.form.get('account_name', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        industry = request.form.get('industry', '').strip()
        
        # Get optional assessor information
        assessor_name = request.form.get('assessor_name', '').strip()
        assessor_email = request.form.get('assessor_email', '').strip()
        
        # Validate required fields
        if not organization_name:
            flash('Organization name is required', 'error')
            return render_template('pages/assessment/org_information.html')
        
        if not account_name:
            flash('Account name is required', 'error')
            return render_template('pages/assessment/org_information.html')
        
        if not first_name or not last_name:
            flash('First name and last name are required', 'error')
            return render_template('pages/assessment/org_information.html')
        
        if not email:
            flash('Email address is required', 'error')
            return render_template('pages/assessment/org_information.html')
        
        if not industry:
            flash('Please select an industry', 'error')
            return render_template('pages/assessment/org_information.html')
        
        # Create assessment using the existing database schema
        from app.extensions import db
        from app.models import Assessment
        from app.models.question import Section
        
        # Get the first section (optionally filtered by ACTIVE_SECTION_IDS)
        sections_q = db.session.query(Section)
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        first_section = sections_q.order_by(Section.display_order).first()
        if not first_section:
            flash('No assessment sections found. Please contact support.', 'error')
            return render_template('pages/assessment/org_information.html')
        
        assessment = Assessment()
        assessment.team_name = account_name
        assessment.organization_name = organization_name
        assessment.account_name = account_name
        assessment.first_name = first_name
        assessment.last_name = last_name
        assessment.email = email
        assessment.industry = industry
        assessment.assessor_name = assessor_name if assessor_name else None
        assessment.assessor_email = assessor_email if assessor_email else None
        assessment.status = 'IN_PROGRESS'
        assessment.created_at = datetime.utcnow()
        assessment.updated_at = datetime.utcnow()
        
        db.session.add(assessment)
        db.session.flush()  # Get the ID without committing yet
        
        # Store the assessment ID before commit
        assessment_id = assessment.id
        
        # Set up comprehensive session management with candidate details BEFORE commit
        manage_assessment_session(assessment_id)
        
        # Initialize response tracking and metadata in session BEFORE commit
        session['assessment_responses'] = {}
        session['assessment_metadata'] = {
            'organization_name': organization_name,
            'account_name': account_name,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'industry': industry,
            'assessor_name': assessor_name,
            'assessor_email': assessor_email,
            'created_at': datetime.utcnow().isoformat(),
            'current_section_index': 0,
            'assessment_id': assessment_id  # Store ID in session for reliability
        }
        
        # Now commit the transaction - everything is set up
        db.session.commit()
        
        # Log successful creation
        logger.info(f"Assessment {assessment_id} successfully created and committed")
        
        logger.info(f"Found first section: {first_section.id} - {first_section.name}")
        flash(f'Assessment created for {first_name} {last_name}. Starting with {first_section.name}!', 'success')
        logger.info(f"Assessment created: {assessment_id} for {organization_name}, proceeding to section {first_section.id}")
        
        # Redirect directly to the first section's questions
        return redirect(url_for('assessment.section_questions', 
                                assessment_id=assessment_id,
                                section_id=first_section.id))
        
    except ValidationError as e:
        flash(f'Validation error: {str(e)}', 'error')
        logger.warning(f"Assessment validation error: {str(e)}")
        return render_template('pages/assessment/org_information.html')
    except AssessmentError as e:
        flash(f'Assessment error: {str(e)}', 'error')
        logger.error(f"Assessment creation error: {str(e)}")
        return render_template('pages/assessment/org_information.html')
    except Exception as e:
        flash('An unexpected error occurred while creating the assessment. Please try again.', 'error')
        try:
            from flask import current_app
            import os
            logger.error(
                "Unexpected error in assessment creation: %s | uri='%s' instance='%s' exists=%s writable=%s",
                e,
                current_app.config.get('SQLALCHEMY_DATABASE_URI'),
                current_app.instance_path,
                os.path.isdir(current_app.instance_path),
                os.access(current_app.instance_path, os.W_OK)
            )
        except Exception:
            logger.error(f"Unexpected error in assessment creation: {str(e)}")
        return render_template('pages/assessment/org_information.html')


@assessment_bp.route('/<int:assessment_id>/section/<section_id>')
def section_questions(assessment_id, section_id):
    """
    Step 3: Questions for a specific section
    """
    try:
        from app.extensions import db
        
        # First try to get the assessment from database
        assessment = db.session.get(Assessment, assessment_id)
        
        # If assessment exists in DB, allow access regardless of session
        if assessment:
            # If assessment is completed, redirect to report
            if assessment.status == 'COMPLETED':
                flash('This assessment has already been completed.', 'info')
                return redirect(url_for('assessment.report', assessment_id=assessment_id))
            
            # If no session metadata but assessment exists, recreate minimal session data
            if 'assessment_metadata' not in session:
                logger.info(f"Recreating session data for existing assessment {assessment_id}")
                session['assessment_metadata'] = {
                    'assessment_id': assessment_id,
                    'organization_name': assessment.organization_name or assessment.team_name or 'Unknown Organization',
                    'account_name': assessment.account_name or '',
                    'first_name': assessment.first_name or '',
                    'last_name': assessment.last_name or '',
                    'email': assessment.email or '',
                    'industry': assessment.industry or '',
                    'assessor_name': assessment.assessor_name or '',
                    'assessor_email': assessment.assessor_email or '',
                    'created_at': assessment.created_at.isoformat() if assessment.created_at else datetime.utcnow().isoformat(),
                    'current_section_index': 0
                }
                session['assessment_responses'] = {}
                # Also set current_assessment_id for consistency with other routes
                session['current_assessment_id'] = assessment_id
                
        else:
            # Assessment doesn't exist in DB, check session for new assessment creation
            if 'assessment_metadata' not in session:
                logger.error(f"No session data and no existing assessment {assessment_id}")
                flash('Assessment session expired. Please start a new assessment.', 'error')
                return redirect(url_for('assessment.create'))
                
            session_assessment_id = session['assessment_metadata'].get('assessment_id')
            if session_assessment_id != assessment_id:
                logger.error(f"Session assessment ID {session_assessment_id} doesn't match URL {assessment_id}")
                flash('Assessment session mismatch. Please start a new assessment.', 'error')
                return redirect(url_for('assessment.create'))
            
            # If no assessment in DB and session is valid, create a temporary assessment object
            logger.warning(f"Assessment {assessment_id} not in DB yet, using session data")
            assessment = type('Assessment', (), {
                'id': assessment_id,
                'team_name': session['assessment_metadata'].get('organization_name'),
                'status': 'IN_PROGRESS'
            })()
        
        # Get section with areas and questions
        section = db.session.query(Section).options(
            joinedload(Section.areas).joinedload(Area.questions)
        ).filter(Section.id == section_id).first()

        # No restriction: any existing section is valid
        
        if not section:
            logger.error(f"Section {section_id} not found")
            flash('Section not found', 'error')
            return redirect(url_for('assessment.create'))
        
        # Get progression data for each area in the section (question-level guidance)
        from app.models.progression import get_all_progressions_for_area
        from app.models.maturity_definition import get_area_definitions
        from app.utils.scoring_utils import SSEConstants
        area_progressions = {}
        area_current_levels = {}
        area_level_defs = {}
        area_domain_details = {}
        # Precompute allowed question ids for the whole app
        all_allowed_ids, _ = _compute_allowed_question_ids(db.session)
        for area in section.areas:
            progressions = get_all_progressions_for_area(area.id)
            # Convert MaturityProgression objects to dictionaries for JSON serialization
            area_progressions[area.id] = {
                level: progression.to_dict() 
                for level, progression in progressions.items()
            }
            # Current level estimation for this area using existing responses
            allowed_area_questions = [q for q in area.questions if q.id in all_allowed_ids]
            total = len(allowed_area_questions)
            yes_count = 0
            if total > 0:
                for q in allowed_area_questions:
                    r = db.session.query(Response).filter(
                        Response.assessment_id == assessment.id,
                        Response.question_id == q.id
                    ).first()
                    if r and getattr(r, 'score', None) is not None and int(r.score) >= 2:
                        yes_count += 1
                pct = yes_count / float(total)
                level = SSEConstants.classify_percentage(pct).value
                # Map to numeric rank
                sse_rank = {'Informal': 1, 'Defined': 2, 'Systematic': 3, 'Integrated': 4, 'Optimized': 5}
                area_current_levels[area.id] = {
                    'level_name': level,
                    'level_num': sse_rank.get(level, 1),
                    'percentage': round(pct * 100.0, 1)
                }
            else:
                area_current_levels[area.id] = {
                    'level_name': 'Informal',
                    'level_num': 1,
                    'percentage': 0.0
                }
            # Fetch area-level maturity definitions for modal rendering (legacy modal)
            defs = get_area_definitions(area.id)
            area_level_defs[area.id] = {lvl: d.to_dict() for (lvl, d) in defs.items()}

            # Fetch area domain-driven details (new modal content)
            try:
                from app.models.area_domain_detail import get_area_domain_detail
                domain = get_area_domain_detail(area.id)
                area_domain_details[area.id] = domain.to_dict() if domain else {}
            except Exception:
                area_domain_details[area.id] = {}
        
        # Get all sections for navigation (optionally filtered)
        all_sections_q = db.session.query(Section)
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            all_sections_q = all_sections_q.filter(Section.id.in_(active_ids))
        all_sections = all_sections_q.order_by(Section.display_order).all()
        
        # Find current section index
        current_section_index = next(
            (i for i, s in enumerate(all_sections) if s.id == section_id), 0
        )
        
        # Update session metadata
        session['assessment_metadata']['current_section_index'] = current_section_index
        session['assessment_metadata']['assessment_id'] = assessment.id
        # Allowed questions: include all active binary items for this section
        all_allowed_ids, _ = _compute_allowed_question_ids(db.session)
        question_ids = []
        allowed_question_ids = set()
        for area in section.areas:
            for q in area.questions:
                question_ids.append(q.id)
                if q.id in all_allowed_ids:
                    allowed_question_ids.add(q.id)
        
        existing_responses = {}
        if question_ids:
            responses = db.session.query(Response).filter(
                Response.assessment_id == assessment_id,
                Response.question_id.in_(question_ids)
            ).all()
            existing_responses = {r.question_id: r for r in responses}
        
        context = {
            'assessment': assessment,
            'section': section,
            'all_sections': all_sections,
            'current_section_index': current_section_index,
            'total_sections': len(all_sections),
            'existing_responses': existing_responses,
            'is_last_section': current_section_index == len(all_sections) - 1,
            'area_progressions': area_progressions,
            'allowed_question_ids': list(allowed_question_ids),
            # New: Area-level maturity definition data and current level estimate
            'area_level_defs': area_level_defs,
            'area_current_levels': area_current_levels,
            'area_domain_details': area_domain_details
        }
        
        return render_template('pages/assessment/section_questions.html', 
                               **context)
        
    except Exception as e:
        logger.error(f"Error loading section questions: {e}")
        flash('Error loading section questions', 'error')
        return redirect(url_for('assessment.detail',
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/section/<section_id>/submit', 
                     methods=['POST'])
def submit_section_responses(assessment_id, section_id):
    """
    Submit all responses for a section
    """
    print(f"DEBUG: Function called with assessment_id={assessment_id}, section_id={section_id}")
    logger.info(f"=== SUBMIT FUNCTION CALLED: assessment_id={assessment_id}, section_id={section_id} ===")
    
    try:
        from app.extensions import db
        
        logger.info(f"Submitting section {section_id} for assessment {assessment_id}")
        
        # Try different approaches to get the assessment
        try:
            # First try: commit and refresh session
            db.session.commit()
            assessment = db.session.query(Assessment).get(assessment_id)
        except:
            # Second try: create new session
            db.session.rollback()
            assessment = db.session.query(Assessment).filter(Assessment.id == assessment_id).first()
        
        if not assessment:
            # Third try: get from session data if it exists
            if 'current_assessment_id' in session and session['current_assessment_id'] == assessment_id:
                # Create a mock assessment object with the data we need
                from app.models.assessment import Assessment as AssessmentModel
                assessment = AssessmentModel()
                assessment.id = assessment_id
                # Get team name from session metadata
                if 'assessment_metadata' in session:
                    assessment.team_name = session['assessment_metadata'].get('organization_name', 'Unknown')
                else:
                    assessment.team_name = 'Unknown'
                assessment.status = 'IN_PROGRESS'
                logger.info(f"Using session data for assessment {assessment_id}")
            else:
                logger.error(f"Assessment {assessment_id} not found anywhere")
                flash('Assessment not found', 'error')
                return redirect(url_for('assessment.index'))
        
        section = db.session.query(Section).get(section_id)
        
        logger.info(f"Assessment query result: {assessment}")
        logger.info(f"Section query result: {section}")
        
        if not assessment:
            logger.error(f"Assessment {assessment_id} not found in database")
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
            
        if not section:
            logger.error(f"Section {section_id} not found in database")
            flash('Section not found', 'error')
            return redirect(url_for('assessment.index'))
        
        logger.info(f"Found assessment: {assessment.team_name}, section: {section.name}")
        
        # Process all responses for this section
        responses_data = {}
        notes_data = {}
        
        # Extract response data from form
        for key, value in request.form.items():
            if key.startswith('response_'):
                question_id = key.replace('response_', '')
                responses_data[question_id] = value
                logger.info(f"Response for {question_id}: {value}")
            elif key.startswith('notes_'):
                question_id = key.replace('notes_', '')
                notes_data[question_id] = value
        
        logger.info(f"Collected {len(responses_data)} responses")
        
        # Save or update responses directly to avoid transaction isolation issues
        for question_id, answer_value in responses_data.items():
            if answer_value:  # Only save if response provided
                # Get notes for this question if present
                notes = notes_data.get(question_id)
                # Check if response already exists
                existing_response = db.session.query(Response).filter(
                    Response.assessment_id == assessment_id,
                    Response.question_id == question_id
                ).first()
                
                if existing_response:
                    # Update existing response
                    existing_response.score = int(answer_value)
                    existing_response.timestamp = datetime.utcnow()
                    if notes is not None:
                        existing_response.notes = notes
                    logger.info(f"Updated response for {question_id}: {answer_value}, notes: {notes}")
                else:
                    # Create new response
                    new_response = Response(
                        assessment_id=assessment_id,
                        question_id=question_id,
                        score=int(answer_value),
                        notes=notes,
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(new_response)
                    logger.info(f"Created new response for {question_id}: {answer_value}, notes: {notes}")
        
        # Commit the responses
        db.session.commit()
        logger.info("All responses committed successfully")
        
        # Update session tracking - ensure session dict exists
        if 'assessment_responses' not in session:
            session['assessment_responses'] = {}
        session['assessment_responses'].update(responses_data)
        
        # Determine next action
        all_sections_q = db.session.query(Section)
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            all_sections_q = all_sections_q.filter(Section.id.in_(active_ids))
        all_sections = all_sections_q.order_by(Section.display_order).all()
        current_index = next(
            (i for i, s in enumerate(all_sections) if s.id == section_id), 0
        )
        
        if current_index < len(all_sections) - 1:
            # Go to next section
            next_section = all_sections[current_index + 1]
            flash(f'Section "{section.name}" completed successfully!', 'success')
            return redirect(url_for('assessment.section_questions',
                                    assessment_id=assessment_id,
                                    section_id=next_section.id))
        else:
            # All sections completed, go to final review
            flash('All sections completed! Ready for final review.', 'success')
            return redirect(url_for('assessment.final_review',
                                    assessment_id=assessment_id))
        
    except Exception as e:
        print(f"DEBUG: Exception in submit_section_responses: {e}")
        logger.error(f"Error submitting section responses: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        flash('Error saving responses. Please try again.', 'error')
        return redirect(url_for('assessment.section_questions',
                                assessment_id=assessment_id,
                                section_id=section_id))


@assessment_bp.route('/<int:assessment_id>/final-review')
def final_review(assessment_id):
    """
    Step 4: Final review before generating report
    """
    try:
        from app.extensions import db
        
        # Get assessment with responses
        assessment = db.session.query(Assessment).get(assessment_id)
        if not assessment:
            # Try session fallback for transaction isolation issues
            assessment_metadata = session.get('assessment_metadata', {})
            if assessment_metadata.get('assessment_id') == assessment_id:
                # Create temporary assessment object for review
                class TempAssessment:
                    def __init__(self, id, team_name, status='IN_PROGRESS'):
                        self.id = id
                        self.team_name = team_name
                        self.status = status
                        self.overall_score = None
                        self.created_at = None
                        self.completion_date = None
                
                assessment = TempAssessment(
                    assessment_id, 
                    assessment_metadata.get('team_name', 'Unknown Organization')
                )
                logger.info(f"Using session data for final review of assessment {assessment_id}")
            else:
                flash('Assessment not found', 'error')
                return redirect(url_for('assessment.index'))
        
        # Get all sections with responses (allowed only)
        sections_q = db.session.query(Section).options(
            joinedload(Section.areas).joinedload(Area.questions)
        )
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        sections = sections_q.order_by(Section.display_order).all()
        
        # Get all responses for this assessment
        responses = db.session.query(Response).filter(
            Response.assessment_id == assessment_id
        ).all()
        responses_dict = {r.question_id: r for r in responses}
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        
        # Calculate completion against constrained logical questions
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        total_questions = len(bin_groups) + (len(allowed_ids) - sum(len(m) for m in bin_groups.values()))
        answered_questions = 0
        for base, members in bin_groups.items():
            if any(mid in responses_dict for mid in members):
                answered_questions += 1
        single_ids = [qid for qid in allowed_ids if not (isinstance(qid, str) and len(qid) >= 3 and qid[-1] in 'ABCDEF' and qid[:-1][-2:].isdigit())]
        for qid in single_ids:
            if qid in responses_dict:
                answered_questions += 1
        
        completion_percentage = (
            (answered_questions / total_questions * 100) 
            if total_questions > 0 else 0
        )
        
        # Get metadata from session or create basic metadata
        metadata = session.get('assessment_metadata', {})
        if not metadata:
            metadata = {
                'team_name': getattr(assessment, 'team_name', 'Organization'),
                'assessment_id': assessment_id,
                'created_at': str(getattr(assessment, 'created_at', '')),
            }
        
        context = {
            'assessment': assessment,
            'sections': sections,
            'responses': responses_dict,
            'metadata': metadata,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'completion_percentage': completion_percentage,
            'can_generate_report': completion_percentage >= 80
        }
        
        logger.info(f"Final review loaded for assessment {assessment_id}, completion: {completion_percentage:.1f}%")
        return render_template('pages/assessment/final_review.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading final review: {e}")
        flash('Error loading final review', 'error')
        return redirect(url_for('assessment.section_questions',
                                assessment_id=assessment_id, section_id='SG'))


@assessment_bp.route('/<int:assessment_id>/generate-report', methods=['POST'])
def generate_report(assessment_id):
    """
    Generate the final assessment report
    """
    try:
        from app.extensions import db
        from sqlalchemy import text
        
        logger.info(f"Starting report generation for assessment {assessment_id}")
        
        # Get assessment using id (schema has been fixed)
        result = db.session.execute(
            text('SELECT * FROM assessments WHERE id = :assessment_id'),
            {'assessment_id': assessment_id}
        )
        assessment_row = result.fetchone()
        
        if not assessment_row:
            logger.error(f"Assessment {assessment_id} not found")
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        logger.info(f"Found assessment {assessment_id}, status: {assessment_row.status}")
        
        # Check if assessment is already completed
        if assessment_row.status == 'COMPLETED':
            flash('Assessment is already completed', 'info')
            return redirect(url_for('assessment.report', 
                                    assessment_id=assessment_id))
        
        # Get responses to check completion
        responses = db.session.query(Response).filter_by(
            assessment_id=assessment_id
        ).all()
        logger.info(f"Found {len(responses)} responses for assessment {assessment_id}")

        # Compute logical totals for constrained flow
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        total_questions = len(bin_groups) + (len(allowed_ids) - sum(len(m) for m in bin_groups.values()))
        responses_dict = {r.question_id: r for r in responses}
        answered_questions = 0
        for base, members in bin_groups.items():
            if any(mid in responses_dict for mid in members):
                answered_questions += 1
        single_ids = [qid for qid in allowed_ids if not (isinstance(qid, str) and len(qid) >= 3 and qid[-1] in 'ABCDEF' and qid[:-1][-2:].isdigit())]
        for qid in single_ids:
            if qid in responses_dict:
                answered_questions += 1
        completion_percentage = (
            (answered_questions / total_questions * 100) 
            if total_questions > 0 else 0
        )
        
        logger.info(
            f"Completion: {answered_questions}/{total_questions} "
            f"({completion_percentage:.1f}%)"
        )
        
        # Check completion requirements
        force_complete = request.form.get('force_complete', 'false') == 'true'
        if not force_complete and completion_percentage < 80:
            flash(
                'Assessment must be at least 80% complete before finalization. '
                'Please answer more questions or use force completion.', 
                'warning'
            )
            return redirect(url_for('assessment.final_review', 
                                    assessment_id=assessment_id))
        
        # Mark assessment as completed and calculate basic scores
        try:
            logger.info(f"Starting completion process for assessment {assessment_id}")
            
            # Get responses by section for scoring (allowed only)
            responses_by_section = {}
            for response in responses:
                if response.question_id not in allowed_ids:
                    continue
                question = db.session.get(Question, response.question_id)
                if question and question.area:
                    section_id = question.area.section_id
                    if section_id not in responses_by_section:
                        responses_by_section[section_id] = []
                    responses_by_section[section_id].append(response)

            # Calculate simple averages per section
            section_scores = {}
            for section_id, section_responses in responses_by_section.items():
                if section_responses:
                    scores = [r.score for r in section_responses if r.score]
                    section_scores[section_id] = (sum(scores) / len(scores) if scores else 0)
            
            logger.info(f"Section scores calculated: {section_scores}")
            
            # Calculate overall score
            scores = [score for score in section_scores.values() if score > 0]
            overall_score = sum(scores) / len(scores) if scores else 0
            
            # Set DevIQ classification based on overall score
            if overall_score >= 3.5:
                deviq_classification = 'Optimized'
            elif overall_score >= 2.5:
                deviq_classification = 'Advanced'
            elif overall_score >= 1.5:
                deviq_classification = 'Evolving'
            else:
                deviq_classification = 'Basic'
            
            logger.info(
                f"Assessment completion data: "
                f"overall_score={overall_score}, "
                f"classification={deviq_classification}"
            )
            
            # Prepare metadata for storage in results_json
            metadata = session.get('assessment_metadata', {})
            assessment_results = {
                'scores': section_scores,
                'overall_score': overall_score,
                'deviq_classification': deviq_classification,
                'metadata': {
                    'organization_name': metadata.get('organization_name'),
                    'account_name': metadata.get('account_name'),
                    'first_name': metadata.get('first_name'),
                    'last_name': metadata.get('last_name'),
                    'email': metadata.get('email'),
                    'industry': metadata.get('industry'),
                    'created_at': metadata.get('created_at'),
                    'completion_date': datetime.utcnow().isoformat()
                }
            }
            
            # Update assessment using raw SQL (since SQLAlchemy model has schema mismatch)
            db.session.execute(text('''
                UPDATE assessments SET 
                    status = 'COMPLETED',
                    completion_date = CURRENT_TIMESTAMP,
                    overall_score = :overall_score,
                    deviq_classification = :deviq_classification,
                    foundational_score = :foundational_score,
                    transformation_score = :transformation_score,
                    enterprise_score = :enterprise_score,
                    governance_score = :governance_score,
                    results_json = :results_json,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :assessment_id
            '''), {
                'overall_score': overall_score,
                'deviq_classification': deviq_classification,
                'foundational_score': section_scores.get('FC', 0),
                'transformation_score': section_scores.get('TC', 0),
                'enterprise_score': section_scores.get('EI', 0),
                'governance_score': section_scores.get('SG', 0),
                'results_json': json.dumps(assessment_results),
                'assessment_id': assessment_id
            })
            
            # Commit the changes
            db.session.commit()
            logger.info(f"Assessment {assessment_id} committed to database")
            
            # Clear session data as assessment is complete
            clear_assessment_session()
            
            logger.info(f"Assessment {assessment_id} completed successfully")
            flash('Assessment completed successfully! Your report is now available.', 'success')
            return redirect(url_for('assessment.report', 
                                    assessment_id=assessment_id))
            
        except Exception as scoring_error:
            logger.error(f"Error during assessment completion: {scoring_error}")
            db.session.rollback()
            flash('Error occurred during completion. Please try again.', 'warning')
            return redirect(url_for('assessment.final_review', 
                                    assessment_id=assessment_id))
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        flash('Error generating report. Please try again.', 'error')
        return redirect(url_for('assessment.final_review', 
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>')
def detail(assessment_id):
    """
    Assessment detail view - redirects to read-only assessment view
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment to verify it exists
        assessment = assessment_service.get_assessment(assessment_id)
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Redirect to read-only organization information view
        return redirect(url_for('assessment.view_readonly',
                                assessment_id=assessment_id))
        
    except Exception as e:
        logger.error(f"Error loading assessment detail: {e}")
        flash('Error loading assessment', 'error')
        return redirect(url_for('assessment.index'))


@assessment_bp.route('/<int:assessment_id>/view')
def view_readonly(assessment_id):
    """
    Read-only view of assessment - organization information page
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment with responses
        assessment = assessment_service.get_assessment(
            assessment_id, include_responses=True
        )
        
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Get progress information
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        context = {
            'assessment': assessment,
            'progress': progress,
            'readonly': True
        }
        
        return render_template('pages/assessment/readonly_org_info.html',
                               **context)
        
    except Exception as e:
        logger.error(f"Error loading assessment readonly view: {e}")
        flash('Error loading assessment', 'error')
        return redirect(url_for('assessment.index'))


@assessment_bp.route('/<int:assessment_id>/view/sections')
def view_readonly_sections(assessment_id):
    """
    Read-only view of assessment - sections overview
    """
    try:
        from app.extensions import db
        
        # Get assessment
        assessment = db.session.query(Assessment).get(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Get all sections with their areas
        sections_q = db.session.query(Section).options(
            joinedload(Section.areas)
        )
        active_ids = _get_active_section_ids(db.session)
        if active_ids:
            sections_q = sections_q.filter(Section.id.in_(active_ids))
        sections = sections_q.order_by(Section.display_order).all()
        
        # Get progress information
        assessment_service = AssessmentService(db.session)
        progress = assessment_service.get_assessment_progress(assessment_id)
        # Logical total questions under constrained flow
        allowed_ids_ro, bin_groups_ro = _compute_allowed_question_ids(db.session)
        logical_total = len(bin_groups_ro) + (len(allowed_ids_ro) - sum(len(v) for v in bin_groups_ro.values()))
        
        context = {
            'assessment': assessment,
            'sections': sections,
            'progress': progress,
            'readonly': True,
            'total_questions': logical_total
        }
        
        return render_template(
            'pages/assessment/readonly_section_overview.html',
            **context)
        
    except Exception as e:
        logger.error(f"Error loading readonly sections overview: {e}")
        flash('Error loading assessment', 'error')
        return redirect(url_for('assessment.index'))


@assessment_bp.route('/<int:assessment_id>/view/section/<section_id>')
def view_readonly_section(assessment_id, section_id):
    """
    Read-only view of assessment - specific section with responses
    """
    try:
        from app.extensions import db
        
        # Get assessment
        assessment = db.session.query(Assessment).get(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Get section with areas and questions
        section = db.session.query(Section).options(
            joinedload(Section.areas).joinedload(Area.questions)
        ).filter(Section.id == section_id).first()
        
        if not section:
            flash('Section not found', 'error')
            return redirect(url_for('assessment.view_readonly_sections',
                                    assessment_id=assessment_id))
        
        # Get all responses for this assessment
        responses = db.session.query(Response).filter(
            Response.assessment_id == assessment_id
        ).all()
        
        # Create responses dictionary for easy lookup
        responses_dict = {resp.question_id: resp for resp in responses}
        
        # Get all sections for navigation
        all_sections = db.session.query(Section).order_by(
            Section.display_order).all()
        
        # Find current section index
        current_section_index = 0
        for i, s in enumerate(all_sections):
            if s.id == section.id:
                current_section_index = i
                break
        
        # Get progress information
        assessment_service = AssessmentService(db.session)
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        context = {
            'assessment': assessment,
            'section': section,
            'responses': responses_dict,
            'all_sections': all_sections,
            'current_section_index': current_section_index,
            'progress': progress,
            'readonly': True
        }
        
        return render_template(
            'pages/assessment/readonly_section_questions.html',
            **context)
        
    except Exception as e:
        logger.error(f"Error loading readonly section view: {e}")
        flash('Error loading section', 'error')
        return redirect(url_for('assessment.view_readonly_sections',
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/question')
@assessment_bp.route('/<int:assessment_id>/question/<question_id>')
def question(assessment_id, question_id=None):
    """
    Assessment question page
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment
        assessment = assessment_service.get_assessment(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Check if assessment is completed
        if assessment.status == 'COMPLETED':
            return redirect(url_for('assessment.report', 
                                    assessment_id=assessment_id))
        
        # Get specific question or next question
        if question_id:
            # IDs are TEXT (e.g., 'ETSI-ESI-01A'); accept string IDs
            question_obj = db.session.query(Question).filter(
                Question.id == str(question_id)
            ).first()
        else:
            question_obj = assessment_service.get_next_question(assessment_id)
        
        if not question_obj:
            # No more questions, redirect to completion
            return redirect(url_for('assessment.complete', 
                                    assessment_id=assessment_id))
        
        # Get existing response if any
        existing_response = db.session.query(Response).filter(
            Response.assessment_id == assessment_id,
            Response.question_id == question_obj.id
        ).first()
        
        # Get progress
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        # Get question navigation context
        all_questions = db.session.query(Question).join(Area).join(
            Section
        ).order_by(
            Section.display_order, Area.display_order, Question.display_order
        ).all()
        
        current_index = next(
            (i for i, q in enumerate(all_questions) if q.id == question_obj.id),
            0
        )
        
        prev_question = all_questions[current_index - 1] if current_index > 0 else None
        next_question_obj = (
            all_questions[current_index + 1] 
            if current_index < len(all_questions) - 1 else None
        )
        
        context = {
            'assessment': assessment,
            'question': question_obj,
            'existing_response': existing_response,
            'progress': progress,
            'current_index': current_index + 1,
            'total_questions': len(all_questions),
            'prev_question': prev_question,
            'next_question': next_question_obj
        }
        
        return render_template('pages/assessment/question.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading question: {e}")
        flash('Error loading question', 'error')
        return redirect(url_for('assessment.detail', 
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/submit', methods=['POST'])
def submit_response(assessment_id):
    """
    Submit a response to an assessment question with enhanced validation 
    and session management
    """
    try:
        # Validate session consistency
        current_assessment = get_current_assessment()
        if current_assessment and current_assessment != assessment_id:
            flash('Session mismatch. Please restart the assessment.', 'warning')
            clear_assessment_session()
            return redirect(url_for('assessment.index'))
        
        assessment_service = get_assessment_service()
        
        # Get form data with validation
        question_id = request.form.get('question_id', type=int)
        answer_value = request.form.get('answer_value', '').strip()
        notes = request.form.get('notes', '').strip()
        next_action = request.form.get('next_action', 'next')
        
        # Validate required fields
        if not question_id:
            flash('Question ID is required', 'error')
            return redirect(url_for('assessment.question', 
                                    assessment_id=assessment_id))
        
        if not answer_value:
            flash('Please select an answer before proceeding', 'error')
            return redirect(url_for('assessment.question', 
                                    assessment_id=assessment_id,
                                    question_id=question_id))
        
        # Validate answer value range
        try:
            answer_int = int(answer_value)
            if answer_int < 1 or answer_int > 5:
                flash('Answer must be between 1 and 5', 'error')
                return redirect(url_for('assessment.question',
                                        assessment_id=assessment_id,
                                        question_id=question_id))
        except ValueError:
            flash('Invalid answer format', 'error')
            return redirect(url_for('assessment.question',
                                    assessment_id=assessment_id,
                                    question_id=question_id))
        
        # Submit response with notes
        response_data = {
            'assessment_id': assessment_id,
            'question_id': question_id,
            'answer_value': answer_value,
            'notes': notes if notes else None
        }
        
        response = assessment_service.submit_response(**response_data)
        
        # Update session tracking
        if 'assessment_responses' not in session:
            session['assessment_responses'] = {}
        session['assessment_responses'][str(question_id)] = {
            'answer_value': answer_value,
            'notes': notes,
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        # Log response submission
        logger.info(f"Response submitted for assessment {assessment_id}, "
                   f"question {question_id}: {answer_value}")
        
        # Handle navigation based on next_action
        return handle_navigation(assessment_id, question_id, next_action)
        
    except ValidationError as e:
        flash(f'Validation error: {str(e)}', 'error')
        logger.warning(f"Response validation error: {str(e)}")
        return redirect(url_for('assessment.question',
                                assessment_id=assessment_id,
                                question_id=question_id))
    except AssessmentError as e:
        flash(f'Assessment error: {str(e)}', 'error')
        logger.error(f"Assessment submission error: {str(e)}")
        return redirect(url_for('assessment.question',
                                assessment_id=assessment_id,
                                question_id=question_id))
    except Exception as e:
        flash('An unexpected error occurred while submitting your response.', 'error')
        logger.error(f"Unexpected error submitting response: {str(e)}")
        return redirect(url_for('assessment.question',
                                assessment_id=assessment_id))


def handle_navigation(assessment_id, current_question_id, next_action):
    """
    Handle assessment navigation after response submission
    
    Args:
        assessment_id: ID of current assessment
        current_question_id: ID of question just answered
        next_action: Navigation action ('next', 'prev', 'complete')
    
    Returns:
        Flask redirect response
    """
    try:
        from app.extensions import db
        assessment_service = get_assessment_service()
        
        if next_action == 'prev':
            # Navigate to previous question
            all_questions = db.session.query(Question).join(Area).join(
                Section
            ).order_by(
                Section.display_order, Area.display_order, Question.display_order
            ).all()
            
            current_index = next(
                (i for i, q in enumerate(all_questions) 
                 if q.id == current_question_id), 0
            )
            
            if current_index > 0:
                prev_question_id = all_questions[current_index - 1].id
                return redirect(url_for('assessment.question',
                                        assessment_id=assessment_id,
                                        question_id=prev_question_id))
            else:
                return redirect(url_for('assessment.question',
                                        assessment_id=assessment_id))
        
        elif next_action == 'complete':
            # Complete assessment
            return redirect(url_for('assessment.complete',
                                    assessment_id=assessment_id))
        
        else:
            # Next question (default)
            next_question = assessment_service.get_next_question(assessment_id)
            if next_question:
                return redirect(url_for('assessment.question',
                                        assessment_id=assessment_id,
                                        question_id=next_question.id))
            else:
                # No more questions, redirect to completion
                return redirect(url_for('assessment.complete',
                                        assessment_id=assessment_id))
    
    except Exception as e:
        logger.error(f"Navigation error: {str(e)}")
        return redirect(url_for('assessment.question',
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/autosave', methods=['POST'])
@csrf.exempt
def autosave_response(assessment_id):
    """
    Autosave a single response (binary Yes/No) and return updated progress.

    Expects JSON payload with:
    - question_id: string question ID
    - score: integer 1 (No) or 2 (Yes)
    - notes: optional string
    """
    try:
        from app.extensions import db

        data = request.get_json(silent=True) or {}
        question_id = str(data.get('question_id', '')).strip()
        score = data.get('score')
        notes = data.get('notes')

        if not question_id or score is None:
            return jsonify({'status': 'error', 'message': 'Missing question_id or score'}), 400

        # Ensure binary score within allowed range (1..2)
        try:
            score_int = int(score)
        except Exception:
            return jsonify({'status': 'error', 'message': 'Invalid score'}), 400
        if score_int not in (1, 2):
            return jsonify({'status': 'error', 'message': 'Score must be 1 or 2'}), 400

        # Upsert response
        existing_response = db.session.query(Response).filter(
            Response.assessment_id == assessment_id,
            Response.question_id == question_id
        ).first()

        if existing_response:
            existing_response.score = score_int
            existing_response.timestamp = datetime.utcnow()
            if notes is not None:
                existing_response.notes = notes
        else:
            new_response = Response(
                assessment_id=assessment_id,
                question_id=question_id,
                score=score_int,
                notes=notes if notes else None,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_response)

        db.session.commit()

        # Calculate updated logical progress using constrained allowed set
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        # All responses for this assessment
        responses = db.session.query(Response).filter(
            Response.assessment_id == assessment_id
        ).all()
        responses_dict = {r.question_id: r for r in responses}

        total_questions = len(bin_groups) + (len(allowed_ids) - sum(len(m) for m in bin_groups.values()))
        answered_questions = 0
        # Count binary groups: answered if any member has a response
        for base, members in bin_groups.items():
            if any(mid in responses_dict for mid in members):
                answered_questions += 1
        # Count single IDs
        single_ids = [qid for qid in allowed_ids if not (isinstance(qid, str) and len(qid) >= 3 and qid[-1] in 'ABCDEF' and qid[:-1][-2:].isdigit())]
        for qid in single_ids:
            if qid in responses_dict:
                answered_questions += 1

        completion_percentage = (answered_questions / total_questions * 100.0) if total_questions > 0 else 0.0

        return jsonify({
            'status': 'success',
            'answered_questions': answered_questions,
            'total_questions': total_questions,
            'progress_percentage': round(completion_percentage, 1)
        })

    except Exception as e:
        logger.error(f"Autosave error: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to autosave response'}), 500


@assessment_bp.route('/<int:assessment_id>/complete')
def complete(assessment_id):
    """
    Complete assessment and show completion page
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment
        assessment = assessment_service.get_assessment(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        # Check if already completed
        if assessment.status == 'COMPLETED':
            return redirect(url_for('assessment.report',
                                    assessment_id=assessment_id))
        
        # Get progress to check if ready for completion
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        context = {
            'assessment': assessment,
            'progress': progress,
            'can_complete': progress['progress_percentage'] >= 80
        }
        
        return render_template('pages/assessment/complete.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading completion page: {e}")
        flash('Error loading completion page', 'error')
        return redirect(url_for('assessment.detail',
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/finalize', methods=['POST'])
def finalize(assessment_id):
    """
    Finalize assessment with complete scoring and recommendation integration
    """
    try:
        # Validate session consistency
        current_assessment = get_current_assessment()
        if current_assessment and current_assessment != assessment_id:
            flash('Session mismatch. Please restart the assessment.', 'warning')
            clear_assessment_session()
            return redirect(url_for('assessment.index'))
        
        assessment_service = get_assessment_service()
        scoring_service = get_scoring_service()
        recommendation_service = get_recommendation_service()
        
        # Get assessment and validate status
        assessment = assessment_service.get_assessment(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        if assessment.status == 'COMPLETED':
            flash('Assessment is already completed', 'info')
            return redirect(url_for('assessment.report',
                                    assessment_id=assessment_id))
        
        # Check completion requirements
        force_complete = request.form.get('force_complete', 'false') == 'true'
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        # Validate completion criteria
        if not force_complete and progress['progress_percentage'] < 80:
            flash('Assessment must be at least 80% complete before finalization. '
                  'Please answer more questions or use force completion.', 'warning')
            return redirect(url_for('assessment.complete',
                                    assessment_id=assessment_id))
        
        # Complete assessment with scoring
        try:
            # Step 1: Mark assessment as completed
            completed_assessment = assessment_service.complete_assessment(
                assessment_id, force=force_complete
            )
            
            # Step 2: Calculate comprehensive scores
            scoring_results = scoring_service.calculate_assessment_score(
                assessment_id
            )
            
            # Step 3: Generate recommendations
            recommendations = recommendation_service.generate_recommendations(
                assessment_id, scoring_results
            )
            
            # Step 4: Update assessment with final results
            assessment_service.update_assessment_results(
                assessment_id,
                scores=scoring_results,
                recommendations=recommendations
            )
            
            # Clear session data as assessment is complete
            clear_assessment_session()
            
            # Log completion
            metadata = session.get('assessment_metadata', {})
            organization = metadata.get('organization', 'Unknown')
            assessor = metadata.get('assessor_name', 'Unknown')
            
            logger.info(f"Assessment {assessment_id} completed successfully "
                       f"for {organization} by {assessor}")
            
            flash('Assessment completed successfully! Your report is now available.', 'success')
            return redirect(url_for('assessment.report',
                                    assessment_id=assessment_id))
            
        except Exception as scoring_error:
            logger.error(f"Error during assessment scoring/completion: {scoring_error}")
            flash('Error occurred during scoring. Assessment saved but may need manual review.', 'warning')
            return redirect(url_for('assessment.report',
                                    assessment_id=assessment_id))
        
    except ValidationError as e:
        flash(f'Validation error: {str(e)}', 'error')
        logger.warning(f"Assessment finalization validation error: {str(e)}")
        return redirect(url_for('assessment.complete',
                                assessment_id=assessment_id))
    except AssessmentError as e:
        flash(f'Assessment error: {str(e)}', 'error')
        logger.error(f"Assessment finalization error: {str(e)}")
        return redirect(url_for('assessment.complete',
                                assessment_id=assessment_id))
    except Exception as e:
        flash('An unexpected error occurred during assessment finalization.', 'error')
        logger.error(f"Unexpected error in assessment finalization: {str(e)}")
        return redirect(url_for('assessment.complete',
                                assessment_id=assessment_id))
        
    except AssessmentError as e:
        flash(f'Error completing assessment: {str(e)}', 'error')
        return redirect(url_for('assessment.complete',
                                assessment_id=assessment_id))
    except Exception as e:
        logger.error(f"Error finalizing assessment: {e}")
        flash('Error finalizing assessment', 'error')
        return redirect(url_for('assessment.complete',
                                assessment_id=assessment_id))





def _calculate_assessment_duration(assessment):
    """
    Calculate assessment duration in human-readable format
    
    Args:
        assessment: Assessment object with created_at and completion_date timestamps
    
    Returns:
        str: Human-readable duration
    """
    try:
        if assessment.completion_date and assessment.created_at:
            duration = assessment.completion_date - assessment.created_at
            total_minutes = int(duration.total_seconds() / 60)
            
            if total_minutes < 60:
                return f"{total_minutes} minutes"
            else:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                if minutes > 0:
                    return f"{hours} hours {minutes} minutes"
                else:
                    return f"{hours} hours"
        
        return "Duration not available"
    except Exception:
        return "Duration not available"


@assessment_bp.route('/<int:assessment_id>/report')
def report(assessment_id):
    """
    Modern, interactive assessment report with charts and roadmap
    """
    try:
        from app.extensions import db
        from sqlalchemy.orm import joinedload
        from app.models.progression import get_all_progressions_for_area
        
        # Get assessment
        assessment = db.session.query(Assessment).get(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        if assessment.status != 'COMPLETED':
            flash('Assessment not completed yet', 'warning')
            return redirect(url_for('assessment.detail',
                                    assessment_id=assessment_id))
        
        # Use scoring service for binary weighted results
        scoring_service = get_scoring_service()
        scoring_results = scoring_service.calculate_assessment_score(assessment_id)

        # Build section breakdown compatible with template expectations
        section_scores = []
        area_scores = {}
        for sec in scoring_results.get('section_scores', {}).values():
            areas_list = []
            for area_key, a in sec.get('area_scores', {}).items():
                areas_list.append({
                    'id': a['area_id'],
                    'name': a['area_name'],
                    'score': a['score'],
                    'level': a.get('sse_level'),
                    'responses_count': a['responses_count'],
                    'domain_normalized': a.get('domain_normalized'),
                    'area_percentage': a.get('area_percentage'),
                })
                area_scores[a['area_id']] = {
                    'score': a['score'],
                    'name': a['area_name'],
                    'responses_count': a['responses_count'],
                    'max_possible': a['total_questions'] * 4
                }
            # Compute section percentage from area percentages
            area_pcts = []
            area_wts = []
            for a in sec.get('area_scores', {}).values():
                pct = a.get('area_percentage')
                if pct is not None:
                    area_pcts.append(pct)
                    from app.utils.scoring_utils import SSEConstants
                    area_wts.append(SSEConstants.AREA_WEIGHTS.get(a['area_id'], a.get('weight', 1.0)))
            section_pct = 0.0
            if area_pcts:
                total_w = sum(area_wts) if area_wts else len(area_pcts)
                section_pct = sum(p * w for p, w in zip(area_pcts, area_wts)) / total_w
            section_sse_level = SSEConstants.classify_percentage(section_pct)
            section_sse = section_sse_level.value
            sse_rank_num = {'Informal': 1, 'Defined': 2, 'Systematic': 3, 'Integrated': 4, 'Optimized': 5}
            section_level_num = sse_rank_num.get(section_sse, 1)

            section_scores.append({
                'id': sec['section_id'],
                'name': sec['section_name'],
                'score': sec['score'],
                'level': section_sse,
                'color': _get_section_color(sec['section_id']),
                'areas': areas_list,
                'responses_count': sec['responses_count'],
                'percentage': round(section_pct * 100.0, 1),
                'level_num': section_level_num
            })

        overall_score = scoring_results.get('deviq_score', 0.0)
        overall_level = scoring_results.get('maturity_level_display', 'Informal')

        # Compute allowed ids and groups for counts
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        responses = db.session.query(Response).filter(
            Response.assessment_id == assessment_id
        ).all()
        responses_dict = {r.question_id: r for r in responses}
        
        # Generate area-level current-state data based on computed domain maturity
        from app.models.maturity_definition import get_area_definition
        from app.models.question import Area
        from app.models.question import Area
        area_roadmap_data = {}
        area_level_cards = {}
        area_domain_details = {}
        area_domain_details = {}
        # Build quick lookup of area responses and gaps (No/unanswered)
        # Collect questions per area that are allowed
        questions_by_area = {}
        for qid in allowed_ids:
            q = db.session.query(Question).get(qid)
            if q and q.area:
                questions_by_area.setdefault(q.area.id, []).append(q)
        # For each section's area in scoring_results, compute recommendations
        sse_rank = {'Informal': 1, 'Defined': 2, 'Systematic': 3, 'Integrated': 4, 'Optimized': 5}
        for sec in scoring_results.get('section_scores', {}).values():
            for _, area in sec.get('area_scores', {}).items():
                area_id = area['area_id']
                area_name = area['area_name']
                # Static descriptive About from Areas table
                area_obj = db.session.query(Area).get(area_id)
                area_description = area_obj.description if area_obj else ''
                # Static descriptive About from Areas table
                area_obj = db.session.query(Area).get(area_id)
                area_description = area_obj.description if area_obj else ''
                current_domain_level_name = area.get('sse_level') or 'Informal'
                current_domain_level = sse_rank.get(current_domain_level_name, 1)
                # Determine gaps: No answers (score==1) or unanswered
                gaps = []
                strengths = []
                for q in questions_by_area.get(area_id, []):
                    r = responses_dict.get(q.id)
                    if not r:
                        gaps.append(q.question)
                    elif hasattr(r, 'score') and int(r.score) >= 2:
                        strengths.append(q.question)
                    else:
                        gaps.append(q.question)
                # Current-level definition card (Area-based, always show)
                cur_def = get_area_definition(area_id, current_domain_level)
                if cur_def:
                    area_level_cards[area_id] = cur_def.to_dict()
                else:
                    area_level_cards[area_id] = None

                area_roadmap_data[area_id] = {
                    'area_name': area_name,
                    'current_level': current_domain_level,
                    'current_level_name': current_domain_level_name,
                    'domain_normalized': area.get('domain_normalized'),
                    'area_description': area_description,
                    'gaps': gaps,
                    'strengths': strengths
                }
                # Fetch domain-driven area details (level-independent)
                try:
                    from app.models.area_domain_detail import get_area_domain_detail
                    domain = get_area_domain_detail(area_id)
                    area_domain_details[area_id] = domain.to_dict() if domain else {}
                except Exception:
                    area_domain_details[area_id] = {}
                # Fetch domain-driven area details (level-independent)
                try:
                    from app.models.area_domain_detail import get_area_domain_detail
                    domain = get_area_domain_detail(area_id)
                    area_domain_details[area_id] = domain.to_dict() if domain else {}
                except Exception:
                    area_domain_details[area_id] = {}
        
        # Prepare chart data
        chart_data = {
            'section_scores': [
                {
                    'name': s['name'],
                    'score': s['score'],
                    'percentage': s['percentage'],
                    'level': s['level'],
                    'level_num': s['level_num'],
                    'color': s['color']
                }
                for s in section_scores
            ],
            'maturity_distribution': _calculate_maturity_distribution(
                section_scores
            ),
            'area_comparison': [
                {
                    'name': area['name'],
                    'score': area['score'],
                    'section': section['name']
                }
                for section in section_scores
                for area in section['areas']
            ]
        }
        
        # Generate insights and recommendations
        insights = _generate_insights(section_scores, overall_score)
        priority_areas = _identify_priority_areas(section_scores)
        
        context = {
            'assessment': assessment,
            'overall_score': overall_score,
            'overall_percentage': scoring_results.get('overall_percentage', 0.0),
            'overall_level': overall_level,
            'section_scores': section_scores,
            'area_scores': area_scores,
            'chart_data': chart_data,
            'area_roadmap_data': area_roadmap_data,
            'area_level_cards': area_level_cards,
            'area_domain_details': area_domain_details,
            'insights': insights,
            'priority_areas': priority_areas,
            'responses_count': len({qid: r for qid, r in responses_dict.items() if qid in allowed_ids}),
            'total_questions': len(allowed_ids),
            'completion_date': assessment.completion_date,
            'organization_name': (
                assessment.organization_name or assessment.team_name
            )
        }
        
        return render_template('pages/assessment/report.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading report: {e}")
        flash('Error loading report', 'error')
        return redirect(url_for('assessment.detail',
                                assessment_id=assessment_id))


def _get_maturity_level_from_score(score):
    """Convert numeric score to maturity level name"""
    if score >= 4.2:
        return 'AI-First'
    elif score >= 3.4:
        return 'AI-Augmented'
    elif score >= 2.6:
        return 'AI-Assisted'
    else:
        return 'Traditional'


def _get_section_color(section_id):
    """Get color for section based on ID"""
    colors = {
        'ET': '#8b5cf6',  # Ethics, Trust and Societal Impact - purple
        'GS': '#2563eb',  # Governance, Strategy and Accountability - blue
        'IA': '#10b981',  # Identity, Autonomy and Access Control - green
        'DP': '#f59e0b',  # Data, Provenance and Third-Party - amber
        'PR': '#ef4444',  # Privacy, User Rights - red
        'TS': '#0ea5e9',  # Technical Security & Ops - sky
        'QE': '#a855f7'   # Quality, Evaluation & Resilience - violet
    }
    return colors.get(section_id, '#6b7280')


def _parse_progression_text(text):
    """Parse progression text into list items"""
    if not text:
        return []
    return [item.strip() for item in text.split('|') if item.strip()]


def _get_level_description(question, level):
    """Get description for specific level of a question"""
    level_descriptions = {
        1: question.level_1_desc,
        2: question.level_2_desc,
        3: question.level_3_desc,
        4: question.level_4_desc
    }
    return level_descriptions.get(level, '')


def _calculate_maturity_distribution(section_scores):
    """Calculate distribution of SSE-CMM maturity levels across sections"""
    distribution = {
        'Informal': 0,
        'Defined': 0,
        'Systematic': 0,
        'Integrated': 0,
        'Optimized': 0
    }
    for section in section_scores:
        level = section.get('level')
        if level in distribution:
            distribution[level] += 1
    return distribution


def _generate_insights(section_scores, overall_score):
    """Generate key insights from the assessment results.

    Updated to use SSE percentage-based scoring (0–100%) rather than
    legacy 0–4.0 numeric values.
    """
    insights = []

    if not section_scores:
        return insights

    # Use percentage (0–100%) as the ranking metric
    strongest = max(section_scores, key=lambda x: x.get('percentage', 0.0))
    weakest = min(section_scores, key=lambda x: x.get('percentage', 0.0))

    insights.append({
        'type': 'strength',
        'title': f"Strongest Area: {strongest['name']}",
        'description': (
            f"Your organization excels in {strongest['name']} "
            f"with confirmed capabilities of {strongest.get('percentage', 0.0):.1f}%"
        ),
        'icon': 'trophy'
    })

    insights.append({
        'type': 'improvement',
        'title': f"Priority for Improvement: {weakest['name']}",
        'description': (
            f"{weakest['name']} shows {weakest.get('percentage', 0.0):.1f}% confirmed capabilities "
            f"and offers the greatest opportunity for advancement"
        ),
        'icon': 'target'
    })

    # Variance insight based on percentage points
    percentages = [s.get('percentage', 0.0) for s in section_scores]
    variance = max(percentages) - min(percentages)

    # Heuristic thresholds for variance on 0–100 scale
    if variance > 20.0:
        insights.append({
            'type': 'warning',
            'title': 'Uneven Maturity Distribution',
            'description': (
                f'Large gap ({variance:.1f} percentage points) between highest and '
                f'lowest scoring areas suggests focused improvement needed'
            ),
            'icon': 'exclamation-triangle'
        })
    elif variance < 5.0:
        insights.append({
            'type': 'success',
            'title': 'Consistent Maturity Levels',
            'description': (
                'Your organization shows consistent maturity across '
                'all assessment areas'
            ),
            'icon': 'check-circle'
        })

    return insights


def _identify_priority_areas(section_scores):
    """Identify priority areas for improvement.

    Updated to use percentage-based scoring with SSE levels.
    """
    if not section_scores:
        return []

    # Sort by percentage ascending to get lowest confirmed capability first
    sorted_sections = sorted(section_scores, key=lambda x: x.get('percentage', 0.0))

    priority_areas = []
    for i, section in enumerate(sorted_sections[:3]):  # Top 3 priority areas
        priority_areas.append({
            'rank': i + 1,
            'name': section['name'],
            'score': section.get('score'),  # kept for backward compatibility
            'percentage': section.get('percentage', 0.0),
            'level': section['level'],
            'color': section['color'],
            'areas': section['areas'][:2],  # Top 2 areas within section
            'improvement_potential': round(max(0.0, 100.0 - section.get('percentage', 0.0)), 1)
        })

    return priority_areas


@assessment_bp.route('/<int:assessment_id>/progress')
def progress(assessment_id):
    """
    Assessment progress page for tracking completion
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment and progress
        assessment = assessment_service.get_assessment(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))
        
        progress_data = assessment_service.get_assessment_progress(
            assessment_id
        )
        
        context = {
            'assessment': assessment,
            'progress': progress_data
        }
        
        return render_template('pages/assessment/progress.html', **context)
        
    except Exception as e:
        logger.error(f"Error loading progress: {e}")
        flash('Error loading progress', 'error')
        return redirect(url_for('assessment.detail',
                                assessment_id=assessment_id))


@assessment_bp.route('/<int:assessment_id>/download-pdf')
def download_pdf(assessment_id):
    """
    Generate and download PDF report
    """
    try:
        from playwright.sync_api import sync_playwright
        from app.extensions import db
        from sqlalchemy.orm import joinedload
        import tempfile
        import os
        
        # Get assessment data (reuse the same logic as report route)
        assessment = db.session.query(Assessment).get(assessment_id)
        if not assessment:
            flash('Assessment not found', 'error')
            return redirect(url_for('assessment.index'))

        if assessment.status != 'COMPLETED':
            flash('Assessment not completed yet', 'warning')
            return redirect(url_for('assessment.detail',
                                    assessment_id=assessment_id))

        # Reuse scoring service and SSE logic from HTML report
        scoring_service = get_scoring_service()
        scoring_results = scoring_service.calculate_assessment_score(assessment_id)

        # Build section breakdown compatible with template expectations (SSE-based)
        section_scores = []
        area_scores = {}
        for sec in scoring_results.get('section_scores', {}).values():
            areas_list = []
            for area_key, a in sec.get('area_scores', {}).items():
                areas_list.append({
                    'id': a['area_id'],
                    'name': a['area_name'],
                    'score': a['score'],
                    'level': a.get('sse_level'),
                    'responses_count': a['responses_count'],
                    'domain_normalized': a.get('domain_normalized'),
                    'area_percentage': a.get('area_percentage'),
                })
                area_scores[a['area_id']] = {
                    'score': a['score'],
                    'name': a['area_name'],
                    'responses_count': a['responses_count'],
                    'max_possible': a['total_questions'] * 4
                }
            # Compute section percentage from area percentages
            area_pcts = []
            area_wts = []
            for a in sec.get('area_scores', {}).values():
                pct = a.get('area_percentage')
                if pct is not None:
                    area_pcts.append(pct)
                    from app.utils.scoring_utils import SSEConstants
                    area_wts.append(SSEConstants.AREA_WEIGHTS.get(a['area_id'], a.get('weight', 1.0)))
            section_pct = 0.0
            if area_pcts:
                total_w = sum(area_wts) if area_wts else len(area_pcts)
                section_pct = sum(p * w for p, w in zip(area_pcts, area_wts)) / total_w
            section_sse_level = SSEConstants.classify_percentage(section_pct)
            section_sse = section_sse_level.value
            sse_rank_num = {'Informal': 1, 'Defined': 2, 'Systematic': 3, 'Integrated': 4, 'Optimized': 5}
            section_level_num = sse_rank_num.get(section_sse, 1)

            section_scores.append({
                'id': sec['section_id'],
                'name': sec['section_name'],
                'score': sec['score'],
                'level': section_sse,
                'color': _get_section_color(sec['section_id']),
                'areas': areas_list,
                'responses_count': sec['responses_count'],
                'percentage': round(section_pct * 100.0, 1),
                'level_num': section_level_num
            })

        overall_score = scoring_results.get('deviq_score', 0.0)
        overall_level = scoring_results.get('maturity_level_display', 'Informal')
        overall_percentage = scoring_results.get('overall_percentage', 0.0)

        # Compute allowed ids and groups for counts
        allowed_ids, bin_groups = _compute_allowed_question_ids(db.session)
        responses = db.session.query(Response).filter(
            Response.assessment_id == assessment_id
        ).all()
        responses_dict = {r.question_id: r for r in responses}

        # Generate area-level current-state data similar to HTML report
        from app.models.maturity_definition import get_area_definition
        area_roadmap_data = {}
        area_level_cards = {}
        # Collect questions per area that are allowed
        questions_by_area = {}
        for qid in allowed_ids:
            q = db.session.query(Question).get(qid)
            if q and q.area:
                questions_by_area.setdefault(q.area.id, []).append(q)
        sse_rank = {'Informal': 1, 'Defined': 2, 'Systematic': 3, 'Integrated': 4, 'Optimized': 5}
        for sec in scoring_results.get('section_scores', {}).values():
            for _, area in sec.get('area_scores', {}).items():
                area_id = area['area_id']
                area_name = area['area_name']
                current_domain_level_name = area.get('sse_level') or 'Informal'
                current_domain_level = sse_rank.get(current_domain_level_name, 1)
                # Determine gaps/strengths from responses
                gaps = []
                strengths = []
                for q in questions_by_area.get(area_id, []):
                    r = responses_dict.get(q.id)
                    if not r:
                        gaps.append(q.question)
                    elif hasattr(r, 'score') and int(r.score) >= 2:
                        strengths.append(q.question)
                    else:
                        gaps.append(q.question)
                cur_def = get_area_definition(area_id, current_domain_level)
                if cur_def:
                    area_level_cards[area_id] = cur_def.to_dict()
                else:
                    area_level_cards[area_id] = None

                area_roadmap_data[area_id] = {
                    'area_name': area_name,
                    'current_level': current_domain_level,
                    'current_level_name': current_domain_level_name,
                    'domain_normalized': area.get('domain_normalized'),
                    'area_description': area_description,
                    'gaps': gaps,
                    'strengths': strengths
                }

        # Generate chart data
        chart_data = {
            'section_scores': [
                {
                    'name': s['name'],
                    'score': s['score'],
                    'percentage': s['percentage'],
                    'level': s['level'],
                    'level_num': s['level_num'],
                    'color': s['color']
                }
                for s in section_scores
            ],
            'maturity_distribution': _calculate_maturity_distribution(section_scores)
        }

        # Generate insights and recommendations
        insights = _generate_insights(section_scores, overall_score)
        priority_areas = _identify_priority_areas(section_scores)

        context = {
            'assessment': assessment,
            'overall_score': overall_score,
            'overall_percentage': overall_percentage,
            'overall_level': overall_level,
            'section_scores': section_scores,
            'area_scores': area_scores,
            'chart_data': chart_data,
            'area_roadmap_data': area_roadmap_data,
            'area_level_cards': area_level_cards,
            'area_domain_details': area_domain_details,
            'insights': insights,
            'priority_areas': priority_areas,
            'responses_count': len({qid: r for qid, r in responses_dict.items() if qid in allowed_ids}),
            'total_questions': len(bin_groups) + (len(allowed_ids) - sum(len(v) for v in bin_groups.values())),
            'completion_date': assessment.completion_date,
            'organization_name': (
                assessment.organization_name or assessment.team_name
            ),
            'is_pdf': True  # Flag to indicate PDF generation
        }

        # Render the same template with PDF-specific styling
        html_content = render_template('pages/assessment/report_pdf.html', **context)
        
        # Generate PDF using Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
            page = browser.new_page()
            
            # Set HTML content
            page.set_content(html_content, wait_until='networkidle')
            
            # Generate PDF with options
            pdf_bytes = page.pdf(
                format='A4',
                margin={
                    'top': '0.75in',
                    'right': '0.75in', 
                    'bottom': '0.75in',
                    'left': '0.75in'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            browser.close()
        
        # Create response with team name in filename
        team_name = assessment.team_name or assessment.organization_name or "Unknown_Team"
        # Clean team name for filename (remove special characters)
        clean_team_name = "".join(c for c in team_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_team_name = clean_team_name.replace(' ', '_')
        
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="AI_Maturity_Assessment_Report_{clean_team_name}.pdf"'
        
        return response
        
    except ImportError as e:
        flash('PDF generation not available. Please install Playwright.', 'error')
        return redirect(url_for('assessment.report', assessment_id=assessment_id))
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        flash('Error generating PDF report', 'error')
        return redirect(url_for('assessment.report', assessment_id=assessment_id))

@assessment_bp.route('/api/<int:assessment_id>/progress')
def api_progress(assessment_id):
    """
    API endpoint for assessment progress
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        progress = assessment_service.get_assessment_progress(assessment_id)
        
        return jsonify({
            'status': 'success',
            'data': progress,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch progress',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@assessment_bp.route('/<int:assessment_id>/delete', methods=['DELETE', 'POST'])
def delete_assessment(assessment_id):
    """
    Delete an assessment and all its related data
    """
    try:
        from app.extensions import db
        assessment_service = AssessmentService(db.session)
        
        # Get assessment to verify it exists and check status
        assessment = assessment_service.get_assessment(assessment_id)
        if not assessment:
            if request.method == 'DELETE' or request.headers.get('Content-Type') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'Assessment not found'
                }), 404
            else:
                flash('Assessment not found', 'error')
                return redirect(url_for('assessment.index'))
        
        # Prevent deletion of completed assessments
        if assessment.status == 'COMPLETED':
            if request.method == 'DELETE' or request.headers.get('Content-Type') == 'application/json':
                return jsonify({
                    'status': 'error',
                    'message': 'Cannot delete completed assessments'
                }), 400
            else:
                flash('Cannot delete completed assessments', 'error')
                return redirect(url_for('assessment.index'))
        
        # Store assessment name for feedback
        assessment_name = assessment.organization_name or assessment.team_name or f"Assessment {assessment_id}"
        
        # Delete the assessment and all related data (responses, etc.)
        # SQLAlchemy will handle cascade deletes based on relationships
        db.session.delete(assessment)
        db.session.commit()
        
        # Clear any session data related to this assessment
        if session.get('current_assessment_id') == assessment_id:
            clear_assessment_session()
        
        logger.info(f"Assessment {assessment_id} ({assessment_name}) deleted successfully")
        
        if request.method == 'DELETE' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'status': 'success',
                'message': f'Assessment "{assessment_name}" deleted successfully'
            })
        else:
            flash(f'Assessment "{assessment_name}" deleted successfully', 'success')
            return redirect(url_for('assessment.index'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting assessment {assessment_id}: {e}")
        
        if request.method == 'DELETE' or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete assessment'
            }), 500
        else:
            flash('Failed to delete assessment', 'error')
            return redirect(url_for('assessment.index'))
