-- =====================================================
-- EXPLAINABILITY SANDBOX DATABASE SCHEMA
-- =====================================================
-- Purpose: Support interactive XAI exploration and human study
-- Tables: sandbox_instances, explanation_ratings
-- =====================================================

-- Table for storing sample instances used in sandbox
CREATE TABLE IF NOT EXISTS sandbox_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    sample_index INTEGER NOT NULL,
    features JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    true_label VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

-- Table for storing explanation ratings (human study data)
CREATE TABLE IF NOT EXISTS explanation_ratings (
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_sandbox_instances_model ON sandbox_instances(model_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_instances_created ON sandbox_instances(created_at);
CREATE INDEX IF NOT EXISTS idx_ratings_model ON explanation_ratings(model_id);
CREATE INDEX IF NOT EXISTS idx_ratings_created ON explanation_ratings(created_at);
CREATE INDEX IF NOT EXISTS idx_ratings_instance ON explanation_ratings(instance_id);

-- Comments for documentation
COMMENT ON TABLE sandbox_instances IS 'Stores test samples used in Explainability Sandbox for reproducibility';
COMMENT ON TABLE explanation_ratings IS 'Stores human interpretability ratings for thesis research';
COMMENT ON COLUMN explanation_ratings.clarity IS 'Rating 1-5: How clear and understandable was the explanation?';
COMMENT ON COLUMN explanation_ratings.trustworthiness IS 'Rating 1-5: How much do you trust this explanation?';
COMMENT ON COLUMN explanation_ratings.actionability IS 'Rating 1-5: Can you take action based on this explanation?';
