-- ============================================================================
-- SUPABASE RESET - DELETE EVERYTHING
-- ============================================================================
-- ⚠️  WARNING: This will DELETE ALL DATA!
-- Run this ONLY if you want to start fresh
-- ============================================================================

-- Drop all views first (they depend on tables)
DROP VIEW IF EXISTS model_leaderboard CASCADE;
DROP VIEW IF EXISTS human_evaluation_summary CASCADE;
DROP VIEW IF EXISTS dataset_statistics CASCADE;

-- Drop all tables in correct order (respects foreign keys)
DROP TABLE IF EXISTS human_evaluations CASCADE;
DROP TABLE IF EXISTS study_questions CASCADE;
DROP TABLE IF EXISTS study_sessions CASCADE;
DROP TABLE IF EXISTS explanations CASCADE;
DROP TABLE IF EXISTS model_metrics CASCADE;
DROP TABLE IF EXISTS benchmarks CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop triggers and functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ All tables, views, and functions deleted!';
    RAISE NOTICE '   You can now run 2_supabase_complete_schema.sql';
END $$;
