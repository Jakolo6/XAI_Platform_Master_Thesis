-- ============================================================
-- XAI RESEARCH PLATFORM - DATABASE SCHEMA
-- Migration: 001_initial_schema
-- Created: 2025-10-10
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- DATASETS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    description TEXT,
    
    -- Source information
    source VARCHAR(50) NOT NULL,  -- 'kaggle', 'upload', 'url'
    source_identifier VARCHAR(255),
    kaggle_dataset VARCHAR(255),
    kaggle_competition VARCHAR(255),
    
    -- Dataset configuration
    target_column VARCHAR(100),
    positive_class VARCHAR(50),
    split_ratios JSONB DEFAULT '{"train": 0.7, "val": 0.15, "test": 0.15}'::jsonb,
    
    -- Preprocessing pipeline
    preprocessing_pipeline JSONB,
    feature_engineering JSONB,
    
    -- Statistics
    total_samples INTEGER,
    num_features INTEGER,
    class_balance JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    -- Metadata
    license VARCHAR(255),
    citation TEXT,
    tags JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- MODELS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    
    -- Dataset reference
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    
    -- Configuration
    hyperparameters JSONB,
    training_config JSONB,
    
    -- Storage
    model_path VARCHAR(500),
    model_hash VARCHAR(64) UNIQUE,
    model_size_mb FLOAT,
    
    -- Training
    training_time_seconds FLOAT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- MODEL METRICS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models(id) ON DELETE CASCADE,
    
    -- Classification metrics
    auc_roc FLOAT,
    auc_pr FLOAT,
    f1_score FLOAT,
    precision FLOAT,
    recall FLOAT,
    accuracy FLOAT,
    log_loss FLOAT,
    brier_score FLOAT,
    
    -- Calibration
    expected_calibration_error FLOAT,
    maximum_calibration_error FLOAT,
    
    -- Confusion matrix
    confusion_matrix JSONB,
    class_metrics JSONB,
    additional_metrics JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- EXPLANATIONS TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    
    -- Method
    method VARCHAR(50) NOT NULL,  -- 'shap' or 'lime'
    type VARCHAR(50) NOT NULL,    -- 'global' or 'local'
    
    -- Summary data (aggregated, not raw)
    summary_json JSONB,
    top_features JSONB,
    feature_importance JSONB,
    
    -- Quality metrics
    faithfulness_score FLOAT,
    robustness_score FLOAT,
    complexity_score FLOAT,
    overall_quality FLOAT,
    
    -- Metadata
    num_samples INTEGER,
    num_features INTEGER,
    computation_time_seconds FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- EXPERIMENTS TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    description TEXT,
    
    dataset_id UUID REFERENCES datasets(id),
    model_id UUID REFERENCES models(id),
    
    config JSONB,
    results JSONB,
    metrics JSONB,
    
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================
-- BENCHMARKS TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    description TEXT,
    
    dataset_ids JSONB,
    model_ids JSONB,
    metrics JSONB,
    
    results JSONB,
    summary JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_datasets_name ON datasets(name);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_is_active ON datasets(is_active);

CREATE INDEX IF NOT EXISTS idx_models_dataset ON models(dataset_id);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);
CREATE INDEX IF NOT EXISTS idx_models_status ON models(status);

CREATE INDEX IF NOT EXISTS idx_metrics_model ON model_metrics(model_id);

CREATE INDEX IF NOT EXISTS idx_explanations_model ON explanations(model_id);
CREATE INDEX IF NOT EXISTS idx_explanations_dataset ON explanations(dataset_id);
CREATE INDEX IF NOT EXISTS idx_explanations_method ON explanations(method);

CREATE INDEX IF NOT EXISTS idx_experiments_dataset ON experiments(dataset_id);
CREATE INDEX IF NOT EXISTS idx_experiments_model ON experiments(model_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE models ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE explanations ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmarks ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for now, refine later for multi-user)
CREATE POLICY "Allow all access to datasets" ON datasets FOR ALL USING (true);
CREATE POLICY "Allow all access to models" ON models FOR ALL USING (true);
CREATE POLICY "Allow all access to metrics" ON model_metrics FOR ALL USING (true);
CREATE POLICY "Allow all access to explanations" ON explanations FOR ALL USING (true);
CREATE POLICY "Allow all access to experiments" ON experiments FOR ALL USING (true);
CREATE POLICY "Allow all access to benchmarks" ON benchmarks FOR ALL USING (true);

-- ============================================================
-- SUCCESS MESSAGE
-- ============================================================
DO $$
BEGIN
    RAISE NOTICE '✅ XAI Platform database schema created successfully!';
    RAISE NOTICE '📊 Tables created: datasets, models, model_metrics, explanations, experiments, benchmarks';
    RAISE NOTICE '🔒 Row Level Security enabled';
    RAISE NOTICE '⚡ Indexes created for performance';
END $$;
