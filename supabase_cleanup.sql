-- ============================================================
-- SUPABASE CLEANUP - Delete All Tables and Start Fresh
-- ============================================================
-- Run this FIRST to clean up any existing tables
-- ============================================================

-- Drop all policies first
DROP POLICY IF EXISTS "Allow all operations on benchmarks" ON benchmarks;
DROP POLICY IF EXISTS "Allow all operations on explanations" ON explanations;
DROP POLICY IF EXISTS "Allow all operations on models" ON models;
DROP POLICY IF EXISTS "Allow all operations on datasets" ON datasets;

-- Drop all tables in reverse order (to handle foreign keys)
DROP TABLE IF EXISTS benchmarks CASCADE;
DROP TABLE IF EXISTS explanations CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;

-- Verify cleanup
SELECT 'Cleanup complete! All tables dropped.' as status;
