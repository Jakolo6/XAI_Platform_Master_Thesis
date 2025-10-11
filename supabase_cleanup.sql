-- ============================================================
-- SUPABASE COMPLETE CLEANUP - Delete ALL Tables and Start Fresh
-- ============================================================
-- Run this FIRST to clean up ALL existing tables (old and new)
-- ============================================================

-- Drop all policies first (new tables)
DROP POLICY IF EXISTS "Allow all operations on benchmarks" ON benchmarks;
DROP POLICY IF EXISTS "Allow all operations on explanations" ON explanations;
DROP POLICY IF EXISTS "Allow all operations on models" ON models;
DROP POLICY IF EXISTS "Allow all operations on datasets" ON datasets;

-- Drop all policies (old tables if they exist)
DROP POLICY IF EXISTS "Allow all operations on experiments" ON experiments;
DROP POLICY IF EXISTS "Allow all operations on model_metrics" ON model_metrics;

-- Drop ALL tables (new and old) in reverse order
DROP TABLE IF EXISTS benchmarks CASCADE;
DROP TABLE IF EXISTS explanations CASCADE;
DROP TABLE IF EXISTS model_metrics CASCADE;  -- Old table
DROP TABLE IF EXISTS experiments CASCADE;     -- Old table
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;

-- Verify cleanup
SELECT 'Cleanup complete! All tables dropped (old and new).' as status;
