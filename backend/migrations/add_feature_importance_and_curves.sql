-- Migration: Add feature_importance to models table and roc_curve/pr_curve to model_metrics table
-- Date: 2025-01-11
-- Description: Adds columns to store feature importance scores and ROC/PR curve data for comprehensive model analysis

-- Add feature_importance column to models table
ALTER TABLE models 
ADD COLUMN IF NOT EXISTS feature_importance JSONB;

-- Add roc_curve and pr_curve columns to model_metrics table
ALTER TABLE model_metrics 
ADD COLUMN IF NOT EXISTS roc_curve JSONB;

ALTER TABLE model_metrics 
ADD COLUMN IF NOT EXISTS pr_curve JSONB;

-- Add comments for documentation
COMMENT ON COLUMN models.feature_importance IS 'Top N feature importance scores as JSON object mapping feature names to normalized importance values';
COMMENT ON COLUMN model_metrics.roc_curve IS 'ROC curve data with fpr, tpr, and thresholds arrays (100 sampled points)';
COMMENT ON COLUMN model_metrics.pr_curve IS 'Precision-Recall curve data with precision, recall, and thresholds arrays (100 sampled points)';

-- Create indexes for better query performance (optional)
CREATE INDEX IF NOT EXISTS idx_models_feature_importance ON models USING GIN (feature_importance);
