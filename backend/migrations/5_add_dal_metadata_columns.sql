-- ============================================================================
-- ADD DAL METADATA COLUMNS
-- ============================================================================
-- This migration adds metadata tracking columns used by the Data Access Layer
-- Run this on your existing Supabase database
-- ============================================================================

-- Add metadata columns to models table
ALTER TABLE models 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS source_module VARCHAR(100);

-- Add metadata columns to model_metrics table
ALTER TABLE model_metrics 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS source_module VARCHAR(100);

-- Add metadata columns to datasets table
ALTER TABLE datasets 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS source_module VARCHAR(100);

-- Add metadata columns to explanations table
ALTER TABLE explanations 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS source_module VARCHAR(100);

-- Create interpretation_feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS interpretation_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interpretation_id VARCHAR(255),
    model_id VARCHAR(255),
    mode VARCHAR(50),
    clarity INTEGER CHECK (clarity >= 1 AND clarity <= 5),
    trustworthiness INTEGER CHECK (trustworthiness >= 1 AND trustworthiness <= 5),
    fairness INTEGER CHECK (fairness >= 1 AND fairness <= 5),
    comments TEXT,
    user_id VARCHAR(255),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source_module VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_models_last_updated ON models(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_models_source_module ON models(source_module);
CREATE INDEX IF NOT EXISTS idx_model_metrics_last_updated ON model_metrics(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_datasets_last_updated ON datasets(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_explanations_last_updated ON explanations(last_updated DESC);
CREATE INDEX IF NOT EXISTS idx_interpretation_feedback_model ON interpretation_feedback(model_id);
CREATE INDEX IF NOT EXISTS idx_interpretation_feedback_created ON interpretation_feedback(created_at DESC);

-- Add comments
COMMENT ON COLUMN models.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN models.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN model_metrics.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN model_metrics.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN datasets.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN datasets.source_module IS 'Module that last updated this record';
COMMENT ON COLUMN explanations.last_updated IS 'Timestamp of last update via DAL';
COMMENT ON COLUMN explanations.source_module IS 'Module that last updated this record';
COMMENT ON TABLE interpretation_feedback IS 'Stores user feedback on LLM-generated interpretations';

-- Verification
DO $$
DECLARE
    models_cols INTEGER;
    metrics_cols INTEGER;
    datasets_cols INTEGER;
    explanations_cols INTEGER;
    feedback_exists BOOLEAN;
BEGIN
    -- Check if columns were added
    SELECT COUNT(*) INTO models_cols
    FROM information_schema.columns
    WHERE table_name = 'models'
    AND column_name IN ('last_updated', 'source_module');
    
    SELECT COUNT(*) INTO metrics_cols
    FROM information_schema.columns
    WHERE table_name = 'model_metrics'
    AND column_name IN ('last_updated', 'source_module');
    
    SELECT COUNT(*) INTO datasets_cols
    FROM information_schema.columns
    WHERE table_name = 'datasets'
    AND column_name IN ('last_updated', 'source_module');
    
    SELECT COUNT(*) INTO explanations_cols
    FROM information_schema.columns
    WHERE table_name = 'explanations'
    AND column_name IN ('last_updated', 'source_module');
    
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'interpretation_feedback'
    ) INTO feedback_exists;
    
    RAISE NOTICE '✅ DAL Metadata Migration Complete!';
    RAISE NOTICE '   Models columns: % / 2', models_cols;
    RAISE NOTICE '   Metrics columns: % / 2', metrics_cols;
    RAISE NOTICE '   Datasets columns: % / 2', datasets_cols;
    RAISE NOTICE '   Explanations columns: % / 2', explanations_cols;
    RAISE NOTICE '   Interpretation feedback table: %', CASE WHEN feedback_exists THEN 'EXISTS' ELSE 'MISSING' END;
    RAISE NOTICE '';
    RAISE NOTICE '🎉 Database ready for DAL operations!';
END $$;
