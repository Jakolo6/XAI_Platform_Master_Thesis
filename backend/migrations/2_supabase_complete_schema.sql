-- ============================================================================
-- SUPABASE COMPLETE SCHEMA - FINAL VERSION
-- ============================================================================
-- Run this AFTER 1_supabase_reset.sql (or on a fresh database)
-- This creates ALL tables, indexes, views, and triggers
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- TABLES
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
    num_samples INTEGER,
    num_features INTEGER,
    num_classes INTEGER,
    class_balance JSONB,
    train_samples INTEGER,
    val_samples INTEGER,
    test_samples INTEGER,
    r2_path VARCHAR(500),
    processed_path VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,
    source VARCHAR(255),
    task_type VARCHAR(50) DEFAULT 'classification',
    target_column VARCHAR(255),
    feature_names JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
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
    completed_at TIMESTAMPTZ
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
    created_at TIMESTAMPTZ DEFAULT NOW()
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
-- INDEXES
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Datasets
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_task_type ON datasets(task_type);

-- Models
CREATE INDEX idx_models_dataset ON models(dataset_id);
CREATE INDEX idx_models_type ON models(model_type);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_created ON models(created_at DESC);
CREATE INDEX idx_models_feature_importance ON models USING GIN (feature_importance);

-- Model Metrics
CREATE INDEX idx_model_metrics_model ON model_metrics(model_id);
CREATE INDEX idx_model_metrics_auc_roc ON model_metrics(auc_roc DESC);

-- Explanations
CREATE INDEX idx_explanations_model ON explanations(model_id);
CREATE INDEX idx_explanations_dataset ON explanations(dataset_id);
CREATE INDEX idx_explanations_method ON explanations(method);
CREATE INDEX idx_explanations_type ON explanations(explanation_type);

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
    d.num_samples,
    d.num_features,
    d.num_classes,
    d.class_balance,
    COUNT(DISTINCT m.id) as num_models,
    COUNT(DISTINCT e.id) as num_explanations,
    MAX(mm.auc_roc) as best_auc_roc,
    AVG(m.training_time_seconds) as avg_training_time
FROM datasets d
LEFT JOIN models m ON d.id = m.dataset_id AND m.status = 'completed'
LEFT JOIN model_metrics mm ON m.id = mm.model_id
LEFT JOIN explanations e ON d.id = e.dataset_id
GROUP BY d.id, d.name, d.num_samples, d.num_features, d.num_classes, d.class_balance;

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

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE datasets IS 'Stores dataset metadata and processing information';
COMMENT ON TABLE models IS 'Stores trained ML models with metadata and performance metrics';
COMMENT ON TABLE model_metrics IS 'Detailed performance metrics for trained models';
COMMENT ON TABLE explanations IS 'Stores SHAP and LIME explanations for models';
COMMENT ON TABLE human_evaluations IS 'Stores participant ratings of explanation quality';
COMMENT ON TABLE study_sessions IS 'Tracks participant study sessions';
COMMENT ON TABLE study_questions IS 'Pool of evaluation instances with pre-computed explanations';

COMMENT ON COLUMN models.feature_importance IS 'Top N feature importance scores as JSON';
COMMENT ON COLUMN model_metrics.roc_curve IS 'ROC curve data with fpr, tpr, thresholds (100 points)';
COMMENT ON COLUMN model_metrics.pr_curve IS 'PR curve data with precision, recall, thresholds (100 points)';
COMMENT ON COLUMN human_evaluations.trust_score IS 'Participant trust rating (1-5 Likert scale)';
COMMENT ON COLUMN human_evaluations.understanding_score IS 'Participant understanding rating (1-5)';
COMMENT ON COLUMN human_evaluations.usefulness_score IS 'Participant usefulness rating (1-5)';

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
        'study_sessions', 'study_questions', 'human_evaluations'
    );
    
    SELECT COUNT(*) INTO view_count
    FROM information_schema.views
    WHERE table_schema = 'public'
    AND table_name IN (
        'model_leaderboard', 'human_evaluation_summary', 'dataset_statistics'
    );
    
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'public';
    
    RAISE NOTICE '✅ Migration complete!';
    RAISE NOTICE '   Tables: % / 8', table_count;
    RAISE NOTICE '   Views: % / 3', view_count;
    RAISE NOTICE '   Indexes: %', index_count;
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Database ready for XAI Platform!';
END $$;
