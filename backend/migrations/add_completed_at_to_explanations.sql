-- Migration: Add completed_at column to explanations table
-- Date: 2025-10-14
-- Purpose: Fix schema mismatch causing explanation generation to fail

ALTER TABLE explanations 
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;

-- Add comment
COMMENT ON COLUMN explanations.completed_at IS 'Timestamp when the explanation generation was completed';
