-- ============================================================
-- SUPABASE TABLE SCHEMAS FOR XAI PLATFORM
-- ============================================================
-- Run this SQL in Supabase SQL Editor to create required tables
-- ============================================================

-- 1. DATASETS TABLE
-- Stores metadata about processed datasets
CREATE TABLE datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    display_name TEXT,
    description TEXT,
    status TEXT DEFAULT 'pending',
    r2_path TEXT,
    total_samples INTEGER DEFAULT 0,
    num_features INTEGER DEFAULT 0,
    train_samples INTEGER DEFAULT 0,
    val_samples INTEGER DEFAULT 0,
    test_samples INTEGER DEFAULT 0,
    class_balance JSONB,
    processing_time_seconds FLOAT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. MODELS TABLE
-- Stores metadata about trained models
CREATE TABLE models (
    id TEXT PRIMARY KEY,
    dataset_id TEXT,
    model_type TEXT NOT NULL,
    model_name TEXT,
    r2_path TEXT,
    
    -- Performance metrics
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    auc_roc FLOAT,
    
    -- Training info
    training_time_seconds FLOAT,
    hyperparameters JSONB,
    feature_importance JSONB,
    
    -- Timestamps
    trained_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

-- 3. EXPLANATIONS TABLE
-- Stores XAI explanation metadata
CREATE TABLE explanations (
    id TEXT PRIMARY KEY,
    model_id TEXT,
    explanation_type TEXT NOT NULL, -- 'shap', 'lime', 'counterfactual'
    r2_path TEXT,
    sample_size INTEGER,
    computation_time_seconds FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_model FOREIGN KEY (model_id) REFERENCES models(id)
);

-- 4. BENCHMARKS TABLE
-- Stores benchmark comparison results
CREATE TABLE benchmarks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    dataset_id TEXT,
    model_ids TEXT[], -- Array of model IDs
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_benchmark_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_models_dataset_id ON models(dataset_id);
CREATE INDEX idx_models_model_type ON models(model_type);
CREATE INDEX idx_explanations_model_id ON explanations(model_id);
CREATE INDEX idx_benchmarks_dataset_id ON benchmarks(dataset_id);

-- Enable Row Level Security (RLS)
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE models ENABLE ROW LEVEL SECURITY;
ALTER TABLE explanations ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmarks ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now, restrict later)
CREATE POLICY "Allow all operations on datasets" ON datasets FOR ALL USING (true);
CREATE POLICY "Allow all operations on models" ON models FOR ALL USING (true);
CREATE POLICY "Allow all operations on explanations" ON explanations FOR ALL USING (true);
CREATE POLICY "Allow all operations on benchmarks" ON benchmarks FOR ALL USING (true);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Run these to verify tables were created successfully

-- Check datasets table
SELECT * FROM datasets LIMIT 1;

-- Check models table
SELECT * FROM models LIMIT 1;

-- Check explanations table
SELECT * FROM explanations LIMIT 1;

-- Check benchmarks table
SELECT * FROM benchmarks LIMIT 1;

-- ============================================================
-- SAMPLE DATA (OPTIONAL - for testing)
-- ============================================================

-- Insert sample dataset metadata
INSERT INTO datasets (id, name, display_name, description, status)
VALUES 
    ('ieee-cis-fraud', 'ieee-cis-fraud', 'IEEE-CIS Fraud Detection', 'IEEE Computational Intelligence Society fraud detection dataset', 'pending'),
    ('givemesomecredit', 'givemesomecredit', 'Give Me Some Credit', 'Credit default prediction dataset', 'pending'),
    ('german-credit', 'german-credit', 'German Credit Risk', 'German credit risk classification dataset', 'pending')
ON CONFLICT (id) DO NOTHING;
