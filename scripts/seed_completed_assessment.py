#!/usr/bin/env python3
"""
Seed a fully completed assessment with pre-defined Yes/No responses.

This script creates a new assessment record and inserts all 83 binary
responses in the exact order the questions appear (by section → area →
display_order).  It then triggers the scoring pipeline so the assessment
is ready for viewing in the report page.

Usage:
    python scripts/seed_completed_assessment.py

The script uses the Flask application context so that all models, DB
session and scoring services are available.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Bootstrap – make sure the project root is on sys.path
# ---------------------------------------------------------------------------
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault("FLASK_ENV", "development")

from app import create_app
from app.extensions import db
from app.models import Assessment, Response, Section, Area, Question

# ---------------------------------------------------------------------------
# Pre-defined responses in the order questions appear
# (section display_order → area display_order → question display_order)
# True  = "Yes" → score 2  (level_2_desc = "Sim")
# False = "No"  → score 1  (level_1_desc = "Não")
# ---------------------------------------------------------------------------
RESPONSES_IN_ORDER: list[bool] = [
    # ETSI – Ethics, Trust and Societal Impact
    # ETSI-ESI (6 questions: 01A–01F)
    False,  # ETSI-ESI-01A
    False,  # ETSI-ESI-01B
    False,  # ETSI-ESI-01C
    False,  # ETSI-ESI-01D
    False,  # ETSI-ESI-01E
    False,  # ETSI-ESI-01F
    # ETSI-ETC (6 questions: 01A–01F)
    False,  # ETSI-ETC-01A
    False,  # ETSI-ETC-01B
    False,  # ETSI-ETC-01C
    False,  # ETSI-ETC-01D
    False,  # ETSI-ETC-01E
    False,  # ETSI-ETC-01F
    # ETSI-BFR (6 questions: 01A–01F)
    False,  # ETSI-BFR-01A
    False,  # ETSI-BFR-01B
    False,  # ETSI-BFR-01C
    False,  # ETSI-BFR-01D
    False,  # ETSI-BFR-01E
    False,  # ETSI-BFR-01F

    # GSA – Governance, Strategy and Accountability
    # GSA-GSC (5 questions: 01A–01E)
    True,   # GSA-GSC-01A
    True,   # GSA-GSC-01B
    True,   # GSA-GSC-01C
    True,   # GSA-GSC-01D
    True,   # GSA-GSC-01E
    # GSA-PLA (5 questions: 01A–01E)
    True,   # GSA-PLA-01A
    False,  # GSA-PLA-01B
    True,   # GSA-PLA-01C
    True,   # GSA-PLA-01D
    True,   # GSA-PLA-01E
    True,   # GSA-CUL-01A  ← NOTE: GSA-CUL starts here
    True,   # GSA-CUL-01B
    # GSA-CUL (5 questions: 01A–01E)  – continued
    False,  # GSA-CUL-01C
    False,  # GSA-CUL-01D
    False,  # GSA-CUL-01E

    # IAA – Identity, Autonomy and Access Control for AI
    # IAA-IGO (4 questions: 01A–01D)
    True,   # IAA-IGO-01A
    True,   # IAA-IGO-01B
    True,   # IAA-IGO-01C
    True,   # IAA-IGO-01D
    True,   # IAA-CSM-01A  ← IAA-CSM starts here
    # IAA-CSM (5 questions: 01A–01E) – continued
    False,  # IAA-CSM-01B
    False,  # IAA-CSM-01C
    False,  # IAA-CSM-01D
    False,  # IAA-CSM-01E
    # IAA-AAP (4 questions: 01A–01D)
    False,  # IAA-AAP-01A
    False,  # IAA-AAP-01B
    False,  # IAA-AAP-01C
    False,  # IAA-AAP-01D

    # DPR – Data and Provenance
    # DPR-IPU (3 questions: 01A–01C)
    True,   # DPR-IPU-01A
    True,   # DPR-IPU-01B
    False,  # DPR-IPU-01C
    # DPR-DGM (5 questions: 01A–01E)
    True,   # DPR-DGM-01A
    True,   # DPR-DGM-01B
    True,   # DPR-DGM-01C
    True,   # DPR-DGM-01D
    True,   # DPR-DGM-01E

    # PUT – Privacy, User Rights and Operational Transparency
    # PUT-PUC (5 questions: 01A–01E)
    True,   # PUT-PUC-01A
    True,   # PUT-PUC-01B
    True,   # PUT-PUC-01C
    True,   # PUT-PUC-01D
    False,  # PUT-PUC-01E

    # TSA – Technical Security, Architecture and AI Operations
    # TSA-TRO (4 questions: 01A–01D)
    True,   # TSA-TRO-01A
    True,   # TSA-TRO-01B
    True,   # TSA-TRO-01C
    True,   # TSA-TRO-01D
    # TSA-SDA (4 questions: 01A–01D)
    False,  # TSA-SDA-01A
    False,  # TSA-SDA-01B
    False,  # TSA-SDA-01C
    True,   # TSA-SDA-01D
    # TSA-DMH (3 questions: 01A–01C)
    False,  # TSA-DMH-01A
    False,  # TSA-DMH-01B
    False,  # TSA-DMH-01C

    # QEI – Quality, Evaluation, Incident Handling and Resilience
    # QEI-TEI (3 questions: 01A–01C)
    True,   # QEI-TEI-01A
    False,  # QEI-TEI-01B
    False,  # QEI-TEI-01C
    # QEI-IEC (5 questions: 01A–01E)
    True,   # QEI-IEC-01A
    True,   # QEI-IEC-01B
    True,   # QEI-IEC-01C
    True,   # QEI-IEC-01D
    True,   # QEI-IEC-01E
    # QEI-OCM (5 questions: 01A–01E)
    False,  # QEI-OCM-01A
    False,  # QEI-OCM-01B
    False,  # QEI-OCM-01C
    True,   # QEI-OCM-01D
    False,  # QEI-OCM-01E
]

# Assessment metadata
ASSESSMENT_INFO = {
    "organization_name": "Segura",
    "account_name": "Pedro",
    "team_name": "QA",
    "first_name": "Pedro",
    "last_name": "Saraiva",
    "email": "psaraiva@segura.security",
    "industry": "Technology",
    "assessor_name": "Pedro Saraiva",
    "assessor_email": "psaraiva@segura.security",
}


def _get_active_section_ids_from_config(app):
    """Read ACTIVE_SECTION_IDS from Flask config (mirrors route helpers)."""
    cfg_val = app.config.get("ACTIVE_SECTION_IDS")
    if isinstance(cfg_val, str) and cfg_val.strip():
        return [s.strip() for s in cfg_val.split(",") if s.strip()]
    if isinstance(cfg_val, (list, tuple)):
        return [str(s).strip() for s in cfg_val if str(s).strip()]
    return None


def get_ordered_questions(session, active_section_ids=None):
    """
    Return all active binary questions in the same order the UI presents them
    (section.display_order → area.display_order → question.display_order).
    """
    from sqlalchemy.orm import joinedload

    query = session.query(Section).options(
        joinedload(Section.areas).joinedload(Area.questions)
    )
    if active_section_ids:
        query = query.filter(Section.id.in_(active_section_ids))
    sections = query.order_by(Section.display_order).all()

    ordered = []
    for section in sections:
        areas_sorted = sorted(section.areas, key=lambda a: a.display_order)
        for area in areas_sorted:
            questions_sorted = sorted(area.questions, key=lambda q: q.display_order)
            for q in questions_sorted:
                if getattr(q, "is_active", 1) and q.is_binary:
                    ordered.append(q)
    return ordered


def seed_assessment():
    """Create a completed assessment with all responses."""
    app = create_app()

    with app.app_context():
        # Determine active sections
        active_ids = _get_active_section_ids_from_config(app)
        if not active_ids:
            active_ids = [
                s.id
                for s in db.session.query(Section)
                .order_by(Section.display_order)
                .all()
            ]

        # Get questions in presentation order
        questions = get_ordered_questions(db.session, active_ids)
        total_q = len(questions)
        total_r = len(RESPONSES_IN_ORDER)

        print(f"📋 Found {total_q} active binary questions in the database")
        print(f"📝 Pre-defined responses provided: {total_r}")

        if total_q != total_r:
            print(
                f"❌ Mismatch: {total_q} questions vs {total_r} responses. "
                "Please verify the response list matches the question set."
            )
            # Print the question IDs for debugging
            print("\nQuestion IDs in order:")
            for i, q in enumerate(questions):
                marker = "Yes" if i < total_r and RESPONSES_IN_ORDER[i] else "No"
                print(f"  {i+1:3d}. {q.id}  → {marker if i < total_r else '???'}")
            sys.exit(1)

        # ----- Create Assessment -----
        now = datetime.utcnow()
        assessment = Assessment(
            organization_name=ASSESSMENT_INFO["organization_name"],
            account_name=ASSESSMENT_INFO["account_name"],
            team_name=ASSESSMENT_INFO["team_name"],
            first_name=ASSESSMENT_INFO["first_name"],
            last_name=ASSESSMENT_INFO["last_name"],
            email=ASSESSMENT_INFO["email"],
            industry=ASSESSMENT_INFO["industry"],
            assessor_name=ASSESSMENT_INFO["assessor_name"],
            assessor_email=ASSESSMENT_INFO["assessor_email"],
            status="IN_PROGRESS",
            created_at=now,
            updated_at=now,
        )
        db.session.add(assessment)
        db.session.flush()  # Get the auto-generated ID

        assessment_id = assessment.id
        print(f"\n✅ Created assessment ID: {assessment_id}")

        # ----- Insert Responses -----
        for idx, (question, answer_yes) in enumerate(
            zip(questions, RESPONSES_IN_ORDER)
        ):
            score = 2 if answer_yes else 1  # 2 = Sim (Yes), 1 = Não (No)
            response = Response(
                assessment_id=assessment_id,
                question_id=question.id,
                score=score,
                timestamp=now,
            )
            db.session.add(response)

        db.session.commit()
        print(f"✅ Inserted {total_q} responses")

        # ----- Trigger Scoring -----
        try:
            from app.services.scoring_service import ScoringService

            scoring_service = ScoringService(db.session)
            scoring_results = scoring_service.calculate_assessment_score(
                assessment_id
            )
            print(f"✅ Scoring completed")

            # Update assessment with results
            assessment.status = "COMPLETED"
            assessment.completion_date = now
            assessment.overall_score = scoring_results.get("overall_score")
            assessment.deviq_classification = scoring_results.get(
                "deviq_classification",
                scoring_results.get("maturity_level"),
            )

            # Store section scores if available
            section_scores = scoring_results.get("section_scores", {})
            if isinstance(section_scores, dict):
                assessment.foundational_score = section_scores.get(
                    "foundational", section_scores.get("ETSI")
                )
                assessment.transformation_score = section_scores.get(
                    "transformation", section_scores.get("GSA")
                )
                assessment.enterprise_score = section_scores.get(
                    "enterprise", section_scores.get("IAA")
                )
                assessment.governance_score = section_scores.get(
                    "governance", section_scores.get("DPR")
                )

            # Store full results as JSON
            import json
            assessment.results_json = json.dumps(scoring_results, default=str)

            db.session.commit()
            print(f"✅ Assessment marked as COMPLETED")
            print(f"\n{'='*60}")
            print(f"🎉 Seed assessment ready!")
            print(f"   Assessment ID : {assessment_id}")
            print(f"   Status        : COMPLETED")
            print(f"   Overall Score : {assessment.overall_score}")
            print(f"   Classification: {assessment.deviq_classification}")
            print(f"{'='*60}")

        except Exception as e:
            # Even if scoring fails, keep the responses committed
            print(f"⚠️  Scoring encountered an error: {e}")
            print("   Responses are saved. Marking as COMPLETED anyway.")
            assessment.status = "COMPLETED"
            assessment.completion_date = now
            db.session.commit()
            print(f"\n{'='*60}")
            print(f"🎉 Seed assessment created (scoring may need manual review)")
            print(f"   Assessment ID : {assessment_id}")
            print(f"   Status        : COMPLETED")
            print(f"{'='*60}")


if __name__ == "__main__":
    seed_assessment()
