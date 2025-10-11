-- Migration: Create human_evaluations table for interpretability study
-- Date: 2025-01-11
-- Description: Stores participant ratings of explanation quality (trust, understanding, usefulness)

-- Create human_evaluations table
CREATE TABLE IF NOT EXISTS human_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participant info
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    participant_code VARCHAR(50), -- Anonymous code for non-registered participants
    
    -- Study context
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID, -- Link to explanations table if exists
    method VARCHAR(50) NOT NULL, -- 'SHAP', 'LIME', 'baseline' (no explanation)
    question_id UUID NOT NULL, -- Unique ID for this evaluation instance
    
    -- Decision context
    prediction_outcome VARCHAR(50), -- e.g., 'fraud', 'legitimate', 'approved', 'denied'
    prediction_confidence FLOAT, -- Model confidence score
    
    -- Ratings (1-5 Likert scale)
    trust_score INTEGER CHECK (trust_score >= 1 AND trust_score <= 5),
    understanding_score INTEGER CHECK (understanding_score >= 1 AND understanding_score <= 5),
    usefulness_score INTEGER CHECK (usefulness_score >= 1 AND usefulness_score <= 5),
    
    -- Additional metrics
    time_spent FLOAT, -- Time in seconds viewing explanation
    explanation_shown BOOLEAN DEFAULT true, -- Whether explanation was visible
    
    -- Optional feedback
    comments TEXT,
    
    -- Metadata
    session_id UUID, -- Group evaluations from same session
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_method CHECK (method IN ('SHAP', 'LIME', 'baseline', 'none'))
);

-- Create study_questions table (pool of evaluation instances)
CREATE TABLE IF NOT EXISTS study_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Model and explanation reference
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID,
    dataset_id VARCHAR(255),
    
    -- Instance data
    instance_index INTEGER, -- Which test instance
    true_label VARCHAR(50), -- Ground truth
    predicted_label VARCHAR(50), -- Model prediction
    prediction_confidence FLOAT,
    
    -- Explanation data (stored as JSON for flexibility)
    shap_explanation JSONB, -- SHAP values and visualization data
    lime_explanation JSONB, -- LIME weights and visualization data
    
    -- Context for participant
    context_description TEXT, -- Human-readable description
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create study_sessions table (track participant sessions)
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participant info
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    participant_code VARCHAR(50),
    
    -- Session metadata
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_questions INTEGER DEFAULT 0,
    completed_questions INTEGER DEFAULT 0,
    
    -- Randomization seed for reproducibility
    randomization_seed INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'in_progress', -- 'in_progress', 'completed', 'abandoned'
    
    CONSTRAINT valid_status CHECK (status IN ('in_progress', 'completed', 'abandoned'))
);

-- Create aggregated results view for researchers
CREATE OR REPLACE VIEW human_evaluation_summary AS
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_human_eval_user ON human_evaluations(user_id);
CREATE INDEX IF NOT EXISTS idx_human_eval_model ON human_evaluations(model_id);
CREATE INDEX IF NOT EXISTS idx_human_eval_method ON human_evaluations(method);
CREATE INDEX IF NOT EXISTS idx_human_eval_session ON human_evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_human_eval_created ON human_evaluations(created_at);

CREATE INDEX IF NOT EXISTS idx_study_questions_model ON study_questions(model_id);
CREATE INDEX IF NOT EXISTS idx_study_questions_active ON study_questions(is_active);

CREATE INDEX IF NOT EXISTS idx_study_sessions_user ON study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_status ON study_sessions(status);

-- Add comments for documentation
COMMENT ON TABLE human_evaluations IS 'Stores participant ratings of explanation quality for human evaluation studies';
COMMENT ON COLUMN human_evaluations.trust_score IS 'Participant rating of trust in model decision (1-5 Likert scale)';
COMMENT ON COLUMN human_evaluations.understanding_score IS 'Participant rating of understanding why decision was made (1-5)';
COMMENT ON COLUMN human_evaluations.usefulness_score IS 'Participant rating of explanation usefulness (1-5)';
COMMENT ON COLUMN human_evaluations.time_spent IS 'Time in seconds participant spent viewing explanation';
COMMENT ON COLUMN human_evaluations.explanation_shown IS 'Whether explanation was visible (for A/B testing)';

COMMENT ON TABLE study_questions IS 'Pool of evaluation instances with pre-computed explanations';
COMMENT ON TABLE study_sessions IS 'Tracks participant study sessions for completion tracking';
COMMENT ON VIEW human_evaluation_summary IS 'Aggregated statistics for researcher analysis';
