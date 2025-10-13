-- =====================================================
-- Interpretation Layer Feedback Table
-- =====================================================
-- Purpose: Store user feedback on LLM vs Rule-based interpretations
-- for master's thesis research on explainability quality

-- Drop table if exists (for clean reinstall)
DROP TABLE IF EXISTS interpretation_feedback CASCADE;

-- Create interpretation_feedback table
CREATE TABLE interpretation_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interpretation_id VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('llm', 'rule-based')),
    
    -- Rating dimensions (1-5 scale)
    clarity INT NOT NULL CHECK (clarity BETWEEN 1 AND 5),
    trustworthiness INT NOT NULL CHECK (trustworthiness BETWEEN 1 AND 5),
    fairness INT NOT NULL CHECK (fairness BETWEEN 1 AND 5),
    
    -- Optional feedback
    comments TEXT,
    
    -- User tracking
    user_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX idx_interpretation_feedback_model_id ON interpretation_feedback(model_id);
CREATE INDEX idx_interpretation_feedback_mode ON interpretation_feedback(mode);
CREATE INDEX idx_interpretation_feedback_user_id ON interpretation_feedback(user_id);
CREATE INDEX idx_interpretation_feedback_created_at ON interpretation_feedback(created_at);

-- Create composite index for analysis queries
CREATE INDEX idx_interpretation_feedback_model_mode ON interpretation_feedback(model_id, mode);

-- Add comments for documentation
COMMENT ON TABLE interpretation_feedback IS 'User feedback on interpretation quality for master thesis research';
COMMENT ON COLUMN interpretation_feedback.mode IS 'Interpretation method: llm (GPT-4) or rule-based (deterministic)';
COMMENT ON COLUMN interpretation_feedback.clarity IS 'How clear and understandable was the explanation? (1-5)';
COMMENT ON COLUMN interpretation_feedback.trustworthiness IS 'How much do you trust this explanation? (1-5)';
COMMENT ON COLUMN interpretation_feedback.fairness IS 'How fair and unbiased does the explanation seem? (1-5)';

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_interpretation_feedback_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_interpretation_feedback_updated_at
    BEFORE UPDATE ON interpretation_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_interpretation_feedback_updated_at();

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON interpretation_feedback TO authenticated;
-- GRANT USAGE ON SEQUENCE interpretation_feedback_id_seq TO authenticated;

-- =====================================================
-- Analysis Views for Research
-- =====================================================

-- View: Average ratings by mode
CREATE OR REPLACE VIEW interpretation_feedback_summary AS
SELECT 
    mode,
    COUNT(*) as total_ratings,
    ROUND(AVG(clarity)::numeric, 2) as avg_clarity,
    ROUND(AVG(trustworthiness)::numeric, 2) as avg_trustworthiness,
    ROUND(AVG(fairness)::numeric, 2) as avg_fairness,
    ROUND(AVG((clarity + trustworthiness + fairness) / 3.0)::numeric, 2) as avg_overall
FROM interpretation_feedback
GROUP BY mode;

COMMENT ON VIEW interpretation_feedback_summary IS 'Summary statistics for comparing LLM vs Rule-based interpretation quality';

-- View: Ratings by model
CREATE OR REPLACE VIEW interpretation_feedback_by_model AS
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

COMMENT ON VIEW interpretation_feedback_by_model IS 'Ratings breakdown by model and interpretation method';

-- View: Recent feedback
CREATE OR REPLACE VIEW interpretation_feedback_recent AS
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

COMMENT ON VIEW interpretation_feedback_recent IS 'Most recent 50 feedback entries for monitoring';

-- =====================================================
-- Sample Data (Optional - for testing)
-- =====================================================

-- Uncomment to insert sample data for testing
/*
INSERT INTO interpretation_feedback (interpretation_id, model_id, mode, clarity, trustworthiness, fairness, comments, user_id) VALUES
('test_llm_1', 'german-credit_xgboost_8d10e541', 'llm', 5, 4, 5, 'Very clear and natural explanation', 'test_user_1'),
('test_rule_1', 'german-credit_xgboost_8d10e541', 'rule-based', 4, 5, 4, 'Structured and consistent', 'test_user_1'),
('test_llm_2', 'german-credit_xgboost_8d10e541', 'llm', 4, 4, 4, 'Good but sometimes verbose', 'test_user_2'),
('test_rule_2', 'german-credit_xgboost_8d10e541', 'rule-based', 5, 5, 5, 'Very predictable and trustworthy', 'test_user_2');
*/

-- =====================================================
-- Verification Queries
-- =====================================================

-- Check table structure
-- SELECT column_name, data_type, is_nullable, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'interpretation_feedback'
-- ORDER BY ordinal_position;

-- Check indexes
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'interpretation_feedback';

-- Test summary view
-- SELECT * FROM interpretation_feedback_summary;
