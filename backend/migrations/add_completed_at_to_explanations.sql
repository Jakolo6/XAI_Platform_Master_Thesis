-- Migration: Add missing columns to explanations table
-- Date: 2025-10-14
-- Purpose: Fix schema mismatch causing explanation generation to fail

-- Add completed_at column
ALTER TABLE explanations 
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

-- Add explanation_data column for storing raw explanation output
ALTER TABLE explanations 
ADD COLUMN IF NOT EXISTS explanation_data JSONB;

-- Add comments
COMMENT ON COLUMN explanations.completed_at IS 'Timestamp when the explanation generation was completed';
COMMENT ON COLUMN explanations.explanation_data IS 'Raw explanation data (SHAP values, LIME weights, etc.)';
