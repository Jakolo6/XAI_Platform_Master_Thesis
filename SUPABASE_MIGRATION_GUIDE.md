# 🗄️ Supabase Migration Guide

## 📋 Overview

This guide explains how to set up your Supabase database with the complete schema for the XAI Platform.

**✅ UPDATED:** This guide now uses the fixed V2 migration that handles existing tables correctly.

---

## ✅ What's Included

The **single, final SQL file** (`supabase_complete_schema_v2.sql`) includes:

### **Tables (8):**
1. ✅ `users` - User authentication and profiles
2. ✅ `datasets` - Dataset metadata and statistics
3. ✅ `models` - Trained ML models with metrics
4. ✅ `model_metrics` - Detailed performance metrics (ROC/PR curves)
5. ✅ `explanations` - SHAP and LIME explanations
6. ✅ `study_sessions` - Human evaluation session tracking
7. ✅ `study_questions` - Pre-computed evaluation instances
8. ✅ `human_evaluations` - Participant ratings

### **Views (3):**
1. ✅ `model_leaderboard` - Ranked models by performance
2. ✅ `human_evaluation_summary` - Aggregated human ratings
3. ✅ `dataset_statistics` - Dataset overview with counts

### **Features:**
- ✅ All indexes for performance
- ✅ Foreign key constraints
- ✅ Check constraints for data validation
- ✅ Triggers for `updated_at` timestamps
- ✅ Comments on all tables and columns
- ✅ Optional RLS (Row Level Security) policies
- ✅ Sample data (commented out)

---

## 🚀 How to Run the Migration

### **Option 1: Supabase Dashboard (Recommended)**

1. **Login to Supabase:**
   - Go to https://app.supabase.com
   - Select your project

2. **Open SQL Editor:**
   - Click "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Copy & Paste:**
   - Open `backend/migrations/supabase_complete_schema_v2.sql`
   - Copy the entire contents
   - Paste into the SQL Editor

4. **Run the Migration:**
   - Click "Run" button (or press Cmd/Ctrl + Enter)
   - Wait for completion (~5-10 seconds)
   - Check for success message: "Migration complete! Created 8 tables"

5. **Verify:**
   - Go to "Table Editor" in left sidebar
   - You should see all 8 tables listed

---

### **Option 2: Supabase CLI**

```bash
# Install Supabase CLI (if not already installed)
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Run migration
supabase db push

# Or run the SQL file directly
psql -h YOUR_DB_HOST -U postgres -d postgres -f backend/migrations/supabase_complete_schema.sql
```

---

### **Option 3: Direct PostgreSQL Connection**

```bash
# Connect to your Supabase PostgreSQL database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run the migration file
\i backend/migrations/supabase_complete_schema.sql

# Exit
\q
```

---

## 🔧 What to Update in Your Code

### **1. No Backend Code Changes Needed! ✅**

The backend code already references these tables correctly. The migration just creates the schema in Supabase.

### **2. Environment Variables (Already Set) ✅**

Your `.env` file should already have:

```env
# Supabase (Already configured)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# PostgreSQL (Railway - separate database)
DATABASE_URL=postgresql://...
```

**Important:** You have **TWO databases:**
- **Railway PostgreSQL** - Primary database for models, metrics, etc.
- **Supabase PostgreSQL** - Secondary database for metadata and storage

### **3. Which Database Does What?**

**Railway PostgreSQL (Primary):**
- ✅ Models table
- ✅ Model metrics table
- ✅ Explanations table
- ✅ Users table
- ✅ Human evaluations table

**Supabase (Secondary):**
- ✅ Dataset metadata
- ✅ Model registry (copy)
- ✅ Cloudflare R2 file references

**Both databases can have the same schema!** The migration file works for both.

---

## 🎯 Do You Need to Run This on Railway Too?

### **Option A: Keep Current Setup (Recommended)**

If your Railway PostgreSQL already has tables, **you don't need to run this migration on Railway**.

Your current setup is working fine!

### **Option B: Sync Both Databases**

If you want both databases to have the exact same schema:

1. **Railway Dashboard:**
   - Go to https://railway.app
   - Select your project
   - Click on PostgreSQL service
   - Click "Connect"
   - Copy the connection string

2. **Run Migration:**
   ```bash
   psql "YOUR_RAILWAY_DATABASE_URL" -f backend/migrations/supabase_complete_schema.sql
   ```

---

## 📊 Verify Migration Success

### **Check Tables:**

```sql
-- List all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Should show:
-- datasets
-- explanations
-- human_evaluations
-- model_metrics
-- models
-- study_questions
-- study_sessions
-- users
```

### **Check Views:**

```sql
-- List all views
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public';

-- Should show:
-- dataset_statistics
-- human_evaluation_summary
-- model_leaderboard
```

### **Check Indexes:**

```sql
-- Count indexes
SELECT COUNT(*) 
FROM pg_indexes 
WHERE schemaname = 'public';

-- Should show: ~25 indexes
```

---

## 🔄 If You Need to Reset

### **Drop All Tables (CAUTION: Deletes all data!)**

```sql
-- Drop all tables in correct order (respects foreign keys)
DROP TABLE IF EXISTS human_evaluations CASCADE;
DROP TABLE IF EXISTS study_questions CASCADE;
DROP TABLE IF EXISTS study_sessions CASCADE;
DROP TABLE IF EXISTS explanations CASCADE;
DROP TABLE IF EXISTS model_metrics CASCADE;
DROP TABLE IF EXISTS models CASCADE;
DROP TABLE IF EXISTS datasets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop views
DROP VIEW IF EXISTS model_leaderboard CASCADE;
DROP VIEW IF EXISTS human_evaluation_summary CASCADE;
DROP VIEW IF EXISTS dataset_statistics CASCADE;

-- Now re-run the migration
```

---

## 📝 Sample Data (Optional)

The migration file includes commented-out sample data for the 3 datasets:
- IEEE-CIS Fraud Detection
- Give Me Some Credit
- German Credit Risk

To insert sample data:

1. Open `supabase_complete_schema.sql`
2. Find section "11. SAMPLE DATA"
3. Uncomment the INSERT statement (remove `/*` and `*/`)
4. Run the migration again

Or run this directly:

```sql
INSERT INTO datasets (id, name, description, num_samples, num_features, num_classes, class_balance, task_type, target_column)
VALUES 
    ('ieee-cis-fraud', 'IEEE-CIS Fraud Detection', 'Credit card fraud detection dataset from Kaggle', 590540, 50, 2, '{"0": 0.965, "1": 0.035}'::jsonb, 'classification', 'isFraud'),
    ('give-me-some-credit', 'Give Me Some Credit', 'Credit default prediction dataset', 150000, 10, 2, '{"0": 0.933, "1": 0.067}'::jsonb, 'classification', 'SeriousDlqin2yrs'),
    ('german-credit', 'German Credit Risk', 'German credit risk assessment dataset', 1000, 20, 2, '{"0": 0.7, "1": 0.3}'::jsonb, 'classification', 'credit_risk')
ON CONFLICT (id) DO NOTHING;
```

---

## 🔐 Row Level Security (Optional)

The migration includes commented-out RLS policies. To enable:

1. Uncomment the RLS section in the SQL file
2. Adjust policies based on your authentication setup
3. Re-run the migration

Example policies included:
- Users can only see their own evaluations
- Researchers can view all data

---

## ✅ Checklist

After running the migration, verify:

- [ ] 8 tables created
- [ ] 3 views created
- [ ] ~25 indexes created
- [ ] Foreign keys working (try inserting test data)
- [ ] Triggers working (updated_at auto-updates)
- [ ] Sample data inserted (if you uncommented it)
- [ ] Backend can connect (test with API call)

---

## 🆘 Troubleshooting

### **Error: "relation already exists"**

**Solution:** Tables already exist. Either:
- Skip the migration (you're good!)
- Drop existing tables first (see "If You Need to Reset")

### **Error: "permission denied"**

**Solution:** Use the service role key, not the anon key:
- In Supabase dashboard, use SQL Editor (has admin permissions)
- Or use `SUPABASE_SERVICE_KEY` in your connection string

### **Error: "syntax error near..."**

**Solution:** Make sure you copied the entire file:
- Check for missing semicolons
- Ensure all `CREATE TABLE` statements are complete

### **Tables created but empty**

**Solution:** This is normal! The migration only creates the schema.
- Data will be populated when you train models
- Or insert sample data manually (see above)

---

## 📞 Summary

**What You Need to Do:**

1. ✅ **Run the migration on Supabase** (Option 1 recommended)
2. ✅ **Verify tables created** (8 tables, 3 views)
3. ✅ **No code changes needed** (backend already compatible)
4. ✅ **Optional: Insert sample data** (for testing)

**What You DON'T Need to Do:**

- ❌ Don't change any backend code
- ❌ Don't update environment variables (already set)
- ❌ Don't run on Railway (unless you want to sync)

**Result:**

Your Supabase database will have the complete schema for:
- Model training and evaluation
- SHAP/LIME explanations
- Human evaluation studies
- Dataset management

**Status: Ready to use! 🎉**

---

**Last Updated:** January 11, 2025  
**File:** `backend/migrations/supabase_complete_schema_v2.sql`  
**Version:** 2.1.0 (Final - Fixed for existing tables)
