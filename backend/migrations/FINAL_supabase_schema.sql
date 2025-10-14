-- ============================================================================
-- SUPABASE FINAL COMPLETE SCHEMA - XAI Finance Platform
-- ============================================================================
-- This is the FINAL consolidated schema including all features:
-- - Core tables (users, datasets, models, metrics, explanations)
-- - Sandbox tables (sandbox_instances, explanation_ratings)
-- - Interpretation feedback (interpretation_feedback)
-- - DAL metadata columns (last_updated, source_module)
-- - All indexes, views, and triggers
-- ============================================================================
-- Run this AFTER 1_supabase_reset.sql (or on a fresh database)
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'researcher',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Datasets
CREATE TABLE datasets (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source VARCHAR(255) NOT NULL,
    source_identifier VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    file_path VARCHAR(500),
    file_size_mb FLOAT,
    total_rows INTEGER,
    total_columns INTEGER,
    train_rows INTEGER,
    val_rows INTEGER,
    test_rows INTEGER,
    fraud_count INTEGER,
    non_fraud_count INTEGER,
    fraud_percentage FLOAT,
    preprocessing_config JSONB,
    feature_names JSONB,
    statistics JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    -- DAL metadata columns
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100)
);

-- Models
CREATE TABLE models (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    dataset_id VARCHAR(255) REFERENCES datasets(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    hyperparameters JSONB,
    training_config JSONB,
    feature_importance JSONB,
    model_path VARCHAR(500),
    model_hash VARCHAR(64) UNIQUE,
    model_size_mb FLOAT,
    training_time_seconds FLOAT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    -- DAL metadata columns
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100)
);

-- Model Metrics
CREATE TABLE model_metrics (
    id VARCHAR(255) PRIMARY KEY,
    model_id VARCHAR(255) REFERENCES models(id) ON DELETE CASCADE,
    auc_roc FLOAT,
    auc_pr FLOAT,
    f1_score FLOAT,
    precision FLOAT,
    recall FLOAT,
    accuracy FLOAT,
    log_loss FLOAT,
    brier_score FLOAT,
    expected_calibration_error FLOAT,
    maximum_calibration_error FLOAT,
    confusion_matrix JSONB,
    roc_curve JSONB,
    pr_curve JSONB,
    class_metrics JSONB,
    additional_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- DAL metadata columns
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100)
);

-- Explanations
CREATE TABLE explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) REFERENCES models(id) ON DELETE CASCADE,
    dataset_id VARCHAR(255) REFERENCES datasets(id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL,
    explanation_type VARCHAR(50) DEFAULT 'global',
    summary_json JSONB,
    top_features JSONB,
    feature_importance JSONB,
    num_samples INTEGER,
    num_features INTEGER,
    generation_time_seconds FLOAT,
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    -- DAL metadata columns
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100)
);

-- ============================================================================
-- HUMAN STUDY TABLES
-- ============================================================================

-- Study Sessions
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    participant_code VARCHAR(50),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_questions INTEGER DEFAULT 0,
    completed_questions INTEGER DEFAULT 0,
    randomization_seed INTEGER,
    status VARCHAR(50) DEFAULT 'in_progress',
    CONSTRAINT valid_session_status CHECK (status IN ('in_progress', 'completed', 'abandoned'))
);

-- Study Questions
CREATE TABLE study_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID,
    dataset_id VARCHAR(255),
    instance_index INTEGER,
    true_label VARCHAR(50),
    predicted_label VARCHAR(50),
    prediction_confidence FLOAT,
    shap_explanation JSONB,
    lime_explanation JSONB,
    context_description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Human Evaluations
CREATE TABLE human_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    participant_code VARCHAR(50),
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID,
    method VARCHAR(50) NOT NULL,
    question_id UUID NOT NULL,
    prediction_outcome VARCHAR(50),
    prediction_confidence FLOAT,
    trust_score INTEGER CHECK (trust_score >= 1 AND trust_score <= 5),
    understanding_score INTEGER CHECK (understanding_score >= 1 AND understanding_score <= 5),
    usefulness_score INTEGER CHECK (usefulness_score >= 1 AND usefulness_score <= 5),
    time_spent FLOAT,
    explanation_shown BOOLEAN DEFAULT true,
    comments TEXT,
    session_id UUID REFERENCES study_sessions(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_eval_method CHECK (method IN ('SHAP', 'LIME', 'baseline', 'none'))
);

-- ============================================================================
-- SANDBOX TABLES
-- ============================================================================

-- Sandbox Instances (for interactive exploration)
CREATE TABLE sandbox_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    sample_index INTEGER NOT NULL,
    features JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    true_label VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Explanation Ratings (sandbox feedback)
CREATE TABLE explanation_ratings (
    id SERIAL PRIMARY KEY,
    rating_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    instance_id VARCHAR(255) NOT NULL,
    clarity INTEGER CHECK (clarity BETWEEN 1 AND 5) NOT NULL,
    trustworthiness INTEGER CHECK (trustworthiness BETWEEN 1 AND 5) NOT NULL,
    actionability INTEGER CHECK (actionability BETWEEN 1 AND 5) NOT NULL,
    shap_method VARCHAR(50) DEFAULT 'shap',
    lime_method VARCHAR(50) DEFAULT 'lime',
    user_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- ============================================================================
-- INTERPRETATION FEEDBACK TABLE
-- ============================================================================

-- Interpretation Feedback (LLM vs Rule-based comparison)
CREATE TABLE interpretation_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interpretation_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('llm', 'rule-based')),
    -- Rating dimensions (1-5 scale)
    clarity INTEGER NOT NULL CHECK (clarity BETWEEN 1 AND 5),
    trustworthiness INTEGER NOT NULL CHECK (trustworthiness BETWEEN 1 AND 5),
    fairness INTEGER NOT NULL CHECK (fairness BETWEEN 1 AND 5),
    -- Optional feedback
    comments TEXT,
    -- User tracking
    user_id VARCHAR(255),
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    -- DAL metadata columns
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Datasets
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_last_updated ON datasets(last_updated DESC);
CREATE INDEX idx_datasets_source_module ON datasets(source_module);

-- Models
CREATE INDEX idx_models_dataset ON models(dataset_id);
CREATE INDEX idx_models_type ON models(model_type);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_created ON models(created_at DESC);
CREATE INDEX idx_models_feature_importance ON models USING GIN (feature_importance);
CREATE INDEX idx_models_last_updated ON models(last_updated DESC);
CREATE INDEX idx_models_source_module ON models(source_module);

-- Model Metrics
CREATE INDEX idx_model_metrics_model ON model_metrics(model_id);
CREATE INDEX idx_model_metrics_auc_roc ON model_metrics(auc_roc DESC);
CREATE INDEX idx_model_metrics_last_updated ON model_metrics(last_updated DESC);

-- Explanations
CREATE INDEX idx_explanations_model ON explanations(model_id);
CREATE INDEX idx_explanations_dataset ON explanations(dataset_id);
CREATE INDEX idx_explanations_method ON explanations(method);
CREATE INDEX idx_explanations_type ON explanations(explanation_type);
CREATE INDEX idx_explanations_last_updated ON explanations(last_updated DESC);

-- Human Evaluations
CREATE INDEX idx_human_eval_user ON human_evaluations(user_id);
CREATE INDEX idx_human_eval_model ON human_evaluations(model_id);
CREATE INDEX idx_human_eval_method ON human_evaluations(method);
CREATE INDEX idx_human_eval_session ON human_evaluations(session_id);
CREATE INDEX idx_human_eval_created ON human_evaluations(created_at);

-- Study Questions
CREATE INDEX idx_study_questions_model ON study_questions(model_id);
CREATE INDEX idx_study_questions_active ON study_questions(is_active);

-- Study Sessions
CREATE INDEX idx_study_sessions_user ON study_sessions(user_id);
CREATE INDEX idx_study_sessions_status ON study_sessions(status);

-- Sandbox Instances
CREATE INDEX idx_sandbox_instances_model ON sandbox_instances(model_id);
CREATE INDEX idx_sandbox_instances_created ON sandbox_instances(created_at);

-- Explanation Ratings
CREATE INDEX idx_ratings_model ON explanation_ratings(model_id);
CREATE INDEX idx_ratings_created ON explanation_ratings(created_at);
CREATE INDEX idx_ratings_instance ON explanation_ratings(instance_id);

-- Interpretation Feedback
CREATE INDEX idx_interpretation_feedback_model ON interpretation_feedback(model_id);
CREATE INDEX idx_interpretation_feedback_mode ON interpretation_feedback(mode);
CREATE INDEX idx_interpretation_feedback_user ON interpretation_feedback(user_id);
CREATE INDEX idx_interpretation_feedback_created ON interpretation_feedback(created_at DESC);
CREATE INDEX idx_interpretation_feedback_model_mode ON interpretation_feedback(model_id, mode);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Model Leaderboard
CREATE VIEW model_leaderboard AS
SELECT 
    m.id,
    m.name,
    m.model_type,
    m.dataset_id,
    mm.auc_roc,
    mm.auc_pr,
    mm.f1_score,
    mm.accuracy,
    mm.precision,
    mm.recall,
    m.training_time_seconds,
    m.model_size_mb,
    m.created_at,
    RANK() OVER (PARTITION BY m.dataset_id ORDER BY mm.auc_roc DESC NULLS LAST) as rank_in_dataset,
    RANK() OVER (ORDER BY mm.auc_roc DESC NULLS LAST) as global_rank
FROM models m
LEFT JOIN model_metrics mm ON m.id = mm.model_id
WHERE m.status = 'completed'
ORDER BY mm.auc_roc DESC NULLS LAST;

-- Human Evaluation Summary
CREATE VIEW human_evaluation_summary AS
SELECT 
    model_id,
    method,
    COUNT(*) as num_evaluations,
    AVG(trust_score) as mean_trust,
    STDDEV(trust_score) as std_trust,
    AVG(understanding_score) as mean_understanding,
    STDDEV(understanding_score) as std_understanding,
    AVG(usefulness_score) as mean_usefulness,
    STDDEV(usefulness_score) as std_usefulness,
    AVG(time_spent) as mean_time_spent,
    AVG((trust_score + understanding_score + usefulness_score) / 3.0) as composite_human_score
FROM human_evaluations
WHERE explanation_shown = true
GROUP BY model_id, method;

-- Dataset Statistics
CREATE VIEW dataset_statistics AS
SELECT 
    d.id,
    d.name,
    d.total_rows,
    d.total_columns,
    d.fraud_count,
    d.non_fraud_count,
    d.fraud_percentage,
    COUNT(DISTINCT m.id) as num_models,
    COUNT(DISTINCT e.id) as num_explanations,
    MAX(mm.auc_roc) as best_auc_roc,
    AVG(m.training_time_seconds) as avg_training_time
FROM datasets d
LEFT JOIN models m ON d.id = m.dataset_id AND m.status = 'completed'
LEFT JOIN model_metrics mm ON m.id = mm.model_id
LEFT JOIN explanations e ON d.id = e.dataset_id
GROUP BY d.id, d.name, d.total_rows, d.total_columns, d.fraud_count, d.non_fraud_count, d.fraud_percentage;

-- Interpretation Feedback Summary
CREATE VIEW interpretation_feedback_summary AS
SELECT 
    mode,
    COUNT(*) as total_ratings,
    ROUND(AVG(clarity)::numeric, 2) as avg_clarity,
    ROUND(AVG(trustworthiness)::numeric, 2) as avg_trustworthiness,
    ROUND(AVG(fairness)::numeric, 2) as avg_fairness,
    ROUND(AVG((clarity + trustworthiness + fairness) / 3.0)::numeric, 2) as avg_overall
FROM interpretation_feedback
GROUP BY mode;

-- Interpretation Feedback by Model
CREATE VIEW interpretation_feedback_by_model AS
SELECT 
    model_id,
    mode,
    COUNT(*) as rating_count,
    ROUND(AVG(clarity)::numeric, 2) as avg_clarity,
    ROUND(AVG(trustworthiness)::numeric, 2) as avg_trustworthiness,
    ROUND(AVG(fairness)::numeric, 2) as avg_fairness
FROM interpretation_feedback
GROUP BY model_id, mode
ORDER BY model_id, mode;

-- Recent Interpretation Feedback
CREATE VIEW interpretation_feedback_recent AS
SELECT 
    id,
    model_id,
    mode,
    clarity,
    trustworthiness,
    fairness,
    ROUND((clarity + trustworthiness + fairness) / 3.0, 2) as overall_score,
    comments,
    created_at
FROM interpretation_feedback
ORDER BY created_at DESC
LIMIT 50;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_explanations_updated_at BEFORE UPDATE ON explanations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_questions_updated_at BEFORE UPDATE ON study_questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interpretation_feedback_updated_at BEFORE UPDATE ON interpretation_feedback
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

-- Tables
COMMENT ON TABLE datasets IS 'Stores dataset metadata and processing information';
COMMENT ON TABLE models IS 'Stores trained ML models with metadata and performance metrics';
COMMENT ON TABLE model_metrics IS 'Detailed performance metrics for trained models';
COMMENT ON TABLE explanations IS 'Stores SHAP and LIME explanations for models';
COMMENT ON TABLE human_evaluations IS 'Stores participant ratings of explanation quality';
COMMENT ON TABLE study_sessions IS 'Tracks participant study sessions';
COMMENT ON TABLE study_questions IS 'Pool of evaluation instances with pre-computed explanations';
COMMENT ON TABLE sandbox_instances IS 'Stores test samples used in Explainability Sandbox for reproducibility';
COMMENT ON TABLE explanation_ratings IS 'Stores human interpretability ratings for thesis research';
COMMENT ON TABLE interpretation_feedback IS 'User feedback on LLM vs Rule-based interpretation quality for master thesis research';

-- Columns
COMMENT ON COLUMN models.feature_importance IS 'Top N feature importance scores as JSON';
COMMENT ON COLUMN models.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN models.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN model_metrics.roc_curve IS 'ROC curve data with fpr, tpr, thresholds (100 points)';
COMMENT ON COLUMN model_metrics.pr_curve IS 'PR curve data with precision, recall, thresholds (100 points)';
COMMENT ON COLUMN model_metrics.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN model_metrics.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN datasets.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN datasets.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN explanations.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN explanations.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN human_evaluations.trust_score IS 'Participant trust rating (1-5 Likert scale)';
COMMENT ON COLUMN human_evaluations.understanding_score IS 'Participant understanding rating (1-5)';
COMMENT ON COLUMN human_evaluations.usefulness_score IS 'Participant usefulness rating (1-5)';
COMMENT ON COLUMN explanation_ratings.clarity IS 'Rating 1-5: How clear and understandable was the explanation?';
COMMENT ON COLUMN explanation_ratings.trustworthiness IS 'Rating 1-5: How much do you trust this explanation?';
COMMENT ON COLUMN explanation_ratings.actionability IS 'Rating 1-5: Can you take action based on this explanation?';
COMMENT ON COLUMN interpretation_feedback.mode IS 'Interpretation method: llm (GPT-4) or rule-based (deterministic)';
COMMENT ON COLUMN interpretation_feedback.clarity IS 'How clear and understandable was the explanation? (1-5)';
COMMENT ON COLUMN interpretation_feedback.trustworthiness IS 'How much do you trust this explanation? (1-5)';
COMMENT ON COLUMN interpretation_feedback.fairness IS 'How fair and unbiased does the explanation seem? (1-5)';

-- Views
COMMENT ON VIEW interpretation_feedback_summary IS 'Summary statistics for comparing LLM vs Rule-based interpretation quality';
COMMENT ON VIEW interpretation_feedback_by_model IS 'Ratings breakdown by model and interpretation method';
COMMENT ON VIEW interpretation_feedback_recent IS 'Most recent 50 feedback entries for monitoring';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

DO $$
DECLARE
    table_count INTEGER;
    view_count INTEGER;
    index_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'users', 'datasets', 'models', 'model_metrics', 'explanations',
        'study_sessions', 'study_questions', 'human_evaluations',
        'sandbox_instances', 'explanation_ratings', 'interpretation_feedback'
    );
    
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views
    WHERE table_schema = 'public'
    AND table_name IN (
        'model_leaderboard', 'human_evaluation_summary', 'dataset_statistics',
        'interpretation_feedback_summary', 'interpretation_feedback_by_model',
        'interpretation_feedback_recent'
    );
    
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';
    
    RAISE NOTICE '✅ FINAL Schema Migration Complete!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Summary:';
    RAISE NOTICE '   Tables: % / 11', table_count;
    RAISE NOTICE '   Views: % / 6', view_count;
    RAISE NOTICE '   Indexes: %', index_count;
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Database ready for XAI Platform with all features!';
    RAISE NOTICE '';
    RAISE NOTICE '✨ Features included:';
    RAISE NOTICE '   - Core ML pipeline (datasets, models, metrics)';
    RAISE NOTICE '   - Explainability (SHAP, LIME)';
    RAISE NOTICE '   - Human study framework';
    RAISE NOTICE '   - Interactive sandbox';
    RAISE NOTICE '   - Interpretation feedback (LLM vs Rule-based)';
    RAISE NOTICE '   - DAL metadata tracking';
END $$;
