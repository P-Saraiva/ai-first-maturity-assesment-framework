-- ========================================
-- AI-First Software Engineering Maturity Assessment Framework
-- Database Schema (DDL Script)
-- ========================================

-- Migration tracking table
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- Core Entity Tables
-- ========================================

-- Sections table - Main assessment categories
CREATE TABLE sections (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    color TEXT DEFAULT '#3b82f6',
    icon TEXT DEFAULT 'fas fa-cog',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Areas table - Sub-categories within sections
CREATE TABLE areas (
    id TEXT PRIMARY KEY,
    section_id TEXT,
    name TEXT,
    description TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    timeline_l1_l2 TEXT,
    timeline_l2_l3 TEXT,
    timeline_l3_l4 TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

-- Questions table - Individual assessment questions
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    area_id TEXT,
    question TEXT,
    level_1_desc TEXT,
    level_2_desc TEXT,
    level_3_desc TEXT,
    level_4_desc TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id)
);

-- Maturity progression details table - Steps to achieve different levels
CREATE TABLE maturity_progressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id TEXT NOT NULL,
    current_level INTEGER NULL CHECK (current_level >= 1 AND current_level <= 3),
    target_level INTEGER NOT NULL CHECK (target_level >= 2 AND target_level <= 4),
    prerequisites TEXT,
    action_items TEXT,
    success_metrics TEXT,
    timeline TEXT,
    common_pitfall TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id),
    UNIQUE(area_id, current_level, target_level)
);

-- Area/Question maturity definitions table - Descriptions of current level characteristics
-- Supports showing the CURRENT level guidance (not next-level roadmap)
CREATE TABLE IF NOT EXISTS maturity_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('area','question')),
    entity_id TEXT NOT NULL,
    maturity_level INTEGER NOT NULL CHECK (maturity_level >= 1 AND maturity_level <= 5),
    title TEXT,
    summary TEXT,
    characteristics TEXT,  -- pipe-delimited list
    expectations TEXT,     -- pipe-delimited list
    guidance TEXT,         -- free text or pipe-delimited
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id, maturity_level)
);

-- ========================================
-- Assessment Tables
-- ========================================

-- Assessments table - Main assessment records
CREATE TABLE assessments (
    id INTEGER NOT NULL PRIMARY KEY,
    team_name VARCHAR(200),
    organization_name VARCHAR(200),
    account_name VARCHAR(200),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200),
    industry VARCHAR(100),
    assessor_name VARCHAR(200),
    assessor_email VARCHAR(200),
    overall_score FLOAT,
    deviq_classification VARCHAR(50),
    completion_date DATETIME,
    results_json TEXT,
    status VARCHAR(20) NOT NULL,
    foundational_score FLOAT,
    transformation_score FLOAT,
    enterprise_score FLOAT,
    governance_score FLOAT,
    assessment_duration_minutes INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT check_assessment_status CHECK (status IN ('IN_PROGRESS', 'COMPLETED', 'DRAFT')),
    CONSTRAINT check_overall_score_positive CHECK (overall_score >= 0),
    CONSTRAINT check_foundational_score_positive CHECK (foundational_score >= 0),
    CONSTRAINT check_transformation_score_positive CHECK (transformation_score >= 0),
    CONSTRAINT check_enterprise_score_positive CHECK (enterprise_score >= 0),
    CONSTRAINT check_governance_score_positive CHECK (governance_score >= 0),
    CONSTRAINT check_duration_positive CHECK (assessment_duration_minutes >= 0)
);

-- Responses table - Individual question responses
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT,
    question_id TEXT,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 4),
    notes TEXT,
    response_time_seconds INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE(assessment_id, question_id)
);

-- Assessment sections table - Section-level scoring
CREATE TABLE assessment_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT,
    section_id TEXT,
    average_score REAL NOT NULL,
    area_scores_json TEXT,
    maturity_level TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    UNIQUE(assessment_id, section_id)
);

-- Assessment recommendations table - Generated recommendations
CREATE TABLE assessment_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id TEXT,
    recommendation_text TEXT,
    priority_level INTEGER DEFAULT 1,
    category TEXT,
    area_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id),
    FOREIGN KEY (area_id) REFERENCES areas(id)
);

-- Assessment exports table - Export tracking
CREATE TABLE assessment_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_ids TEXT,
    export_type TEXT,
    file_path TEXT,
    exported_by TEXT,
    export_parameters_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
);

-- ========================================
-- Analytics Tables
-- ========================================

-- Analytics summary table - Daily analytics aggregation
CREATE TABLE analytics_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_date DATE NOT NULL,
    total_assessments INTEGER DEFAULT 0,
    completed_assessments INTEGER DEFAULT 0,
    average_overall_score REAL,
    unique_teams INTEGER DEFAULT 0,
    traditional_count INTEGER DEFAULT 0,
    assisted_count INTEGER DEFAULT 0,
    augmented_count INTEGER DEFAULT 0,
    ai_first_count INTEGER DEFAULT 0,
    avg_foundational_score REAL,
    avg_transformation_score REAL,
    avg_enterprise_score REAL,
    avg_governance_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(summary_date)
);

-- Question analytics table - Per-question performance metrics
CREATE TABLE question_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT,
    analysis_date DATE NOT NULL,
    total_responses INTEGER DEFAULT 0,
    average_score REAL,
    level_1_count INTEGER DEFAULT 0,
    level_2_count INTEGER DEFAULT 0,
    level_3_count INTEGER DEFAULT 0,
    level_4_count INTEGER DEFAULT 0,
    avg_response_time_seconds INTEGER,
    notes_percentage REAL,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    UNIQUE(question_id, analysis_date)
);

-- Team progress table - Team improvement tracking
CREATE TABLE team_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT,
    first_assessment_date DATETIME,
    latest_assessment_date DATETIME,
    total_assessments INTEGER DEFAULT 0,
    first_overall_score REAL,
    latest_overall_score REAL,
    best_overall_score REAL,
    improvement_trend TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_name)
);

-- ========================================
-- Views
-- ========================================

-- Assessment overview view - Comprehensive assessment summary
CREATE VIEW v_assessment_overview AS 
SELECT 
    a.id,
    a.team_name,
    a.organization_name,
    a.account_name,
    a.first_name,
    a.last_name,
    a.email,
    a.industry,
    a.assessor_name,
    a.assessor_email,
    a.overall_score,
    a.deviq_classification,
    a.completion_date,
    a.foundational_score,
    a.transformation_score,
    a.enterprise_score,
    a.governance_score,
    COUNT(r.id) as total_responses,
    AVG(r.response_time_seconds) as avg_response_time,
    COUNT(CASE WHEN r.notes IS NOT NULL AND r.notes != '' THEN 1 END) as responses_with_notes
FROM assessments a 
LEFT JOIN responses r ON a.id = r.assessment_id 
WHERE a.status = 'COMPLETED' 
GROUP BY a.id, a.team_name, a.organization_name, a.account_name, a.first_name, a.last_name, 
         a.email, a.industry, a.assessor_name, a.assessor_email, a.overall_score, 
         a.deviq_classification, a.completion_date, a.foundational_score, 
         a.transformation_score, a.enterprise_score, a.governance_score;

-- Section performance view - Performance metrics by section
CREATE VIEW v_section_performance AS 
SELECT 
    s.id as section_id,
    s.name as section_name,
    s.color as section_color,
    COUNT(DISTINCT a.id) as total_assessments,
    AVG(
        CASE s.id 
            WHEN 'FC' THEN a.foundational_score 
            WHEN 'TC' THEN a.transformation_score 
            WHEN 'EI' THEN a.enterprise_score 
            WHEN 'SG' THEN a.governance_score 
        END
    ) as average_score,
    MIN(
        CASE s.id 
            WHEN 'FC' THEN a.foundational_score 
            WHEN 'TC' THEN a.transformation_score 
            WHEN 'EI' THEN a.enterprise_score 
            WHEN 'SG' THEN a.governance_score 
        END
    ) as min_score,
    MAX(
        CASE s.id 
            WHEN 'FC' THEN a.foundational_score 
            WHEN 'TC' THEN a.transformation_score 
            WHEN 'EI' THEN a.enterprise_score 
            WHEN 'SG' THEN a.governance_score 
        END
    ) as max_score
FROM sections s 
CROSS JOIN assessments a 
WHERE a.status = 'COMPLETED' 
GROUP BY s.id, s.name, s.color, s.display_order 
ORDER BY s.display_order;

-- Question difficulty view - Question performance and difficulty analysis
CREATE VIEW v_question_difficulty AS 
SELECT 
    q.id as question_id,
    q.question,
    a.name as area_name,
    s.name as section_name,
    COUNT(r.id) as total_responses,
    AVG(r.score) as average_score,
    COUNT(CASE WHEN r.score = 1 THEN 1 END) as level_1_count,
    COUNT(CASE WHEN r.score = 2 THEN 1 END) as level_2_count,
    COUNT(CASE WHEN r.score = 3 THEN 1 END) as level_3_count,
    COUNT(CASE WHEN r.score = 4 THEN 1 END) as level_4_count,
    CASE 
        WHEN AVG(r.score) < 2.0 THEN 'High' 
        WHEN AVG(r.score) < 2.5 THEN 'Medium' 
        ELSE 'Low' 
    END as difficulty_level
FROM questions q 
JOIN areas a ON q.area_id = a.id 
JOIN sections s ON a.section_id = s.id 
LEFT JOIN responses r ON q.id = r.question_id 
WHERE q.is_active = 1 
GROUP BY q.id, q.question, a.name, s.name, q.display_order 
ORDER BY s.display_order, a.display_order, q.display_order;

-- Maturity distribution view - Overall maturity level distribution
CREATE VIEW v_maturity_distribution AS 
SELECT 
    COUNT(*) as total_assessments,
    COUNT(CASE WHEN overall_score BETWEEN 1.0 AND 1.7 THEN 1 END) as traditional_count,
    COUNT(CASE WHEN overall_score BETWEEN 1.8 AND 2.4 THEN 1 END) as assisted_count,
    COUNT(CASE WHEN overall_score BETWEEN 2.5 AND 3.2 THEN 1 END) as augmented_count,
    COUNT(CASE WHEN overall_score BETWEEN 3.3 AND 4.0 THEN 1 END) as ai_first_count,
    ROUND(COUNT(CASE WHEN overall_score BETWEEN 1.0 AND 1.7 THEN 1 END) * 100.0 / COUNT(*), 2) as traditional_percentage,
    ROUND(COUNT(CASE WHEN overall_score BETWEEN 1.8 AND 2.4 THEN 1 END) * 100.0 / COUNT(*), 2) as assisted_percentage,
    ROUND(COUNT(CASE WHEN overall_score BETWEEN 2.5 AND 3.2 THEN 1 END) * 100.0 / COUNT(*), 2) as augmented_percentage,
    ROUND(COUNT(CASE WHEN overall_score BETWEEN 3.3 AND 4.0 THEN 1 END) * 100.0 / COUNT(*), 2) as ai_first_percentage,
    AVG(overall_score) as overall_average_score
FROM assessments 
WHERE status = 'COMPLETED' AND overall_score IS NOT NULL;

-- ========================================
-- Indexes for Performance Optimization
-- ========================================

-- Core entity indexes
CREATE INDEX idx_areas_section ON areas(section_id, display_order);
CREATE INDEX idx_questions_area ON questions(area_id, display_order);
CREATE INDEX idx_questions_active ON questions(is_active, display_order);

-- Assessment indexes
CREATE INDEX idx_assessments_status ON assessments(status, created_at);
CREATE INDEX idx_assessments_team ON assessments(team_name, created_at);
CREATE INDEX idx_assessments_organization ON assessments(organization_name, created_at);
CREATE INDEX idx_assessments_assessor ON assessments(assessor_name, created_at);
CREATE INDEX idx_assessments_completion ON assessments(completion_date DESC);
CREATE INDEX idx_assessments_score ON assessments(overall_score, deviq_classification);
CREATE INDEX idx_assessments_team_score ON assessments(team_name, overall_score, completion_date);
CREATE INDEX idx_assessments_industry ON assessments(industry, overall_score);

-- Response indexes
CREATE INDEX idx_responses_assessment ON responses(assessment_id, question_id);
CREATE INDEX idx_responses_question ON responses(question_id, score);
CREATE INDEX idx_responses_timestamp ON responses(timestamp);
CREATE INDEX idx_responses_score_analysis ON responses(question_id, score, timestamp);

-- Assessment section indexes
CREATE INDEX idx_assessment_sections_assessment ON assessment_sections(assessment_id, section_id);
CREATE INDEX idx_assessment_sections_score ON assessment_sections(section_id, average_score);

-- Recommendation indexes
CREATE INDEX idx_recommendations_assessment ON assessment_recommendations(assessment_id, priority_level);
CREATE INDEX idx_recommendations_area ON assessment_recommendations(area_id, priority_level);

-- Export indexes
CREATE INDEX idx_exports_created ON assessment_exports(created_at);
CREATE INDEX idx_exports_expires ON assessment_exports(expires_at);

-- Analytics indexes
CREATE INDEX idx_analytics_summary_date ON analytics_summary(summary_date);
CREATE INDEX idx_question_analytics_date ON question_analytics(analysis_date, question_id);
CREATE INDEX idx_team_progress_team ON team_progress(team_name);
CREATE INDEX idx_team_progress_improvement ON team_progress(latest_overall_score DESC);

-- Maturity progression indexes
CREATE INDEX idx_progressions_area ON maturity_progressions(area_id, target_level);
CREATE INDEX idx_progressions_level ON maturity_progressions(target_level);
CREATE INDEX idx_progressions_area_from_to ON maturity_progressions(area_id, current_level, target_level);

-- Maturity definitions indexes
CREATE INDEX IF NOT EXISTS idx_maturity_def_entity ON maturity_definitions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_maturity_def_level ON maturity_definitions(maturity_level);

-- ========================================
-- End of Schema
-- ========================================
